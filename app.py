from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json, os, re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ai_driven_coach_secret_key"
CORS(app)

USER_DB = 'users.json'

ROLE_QUESTIONS = {
    "Software Engineer": ["Explain the concept of Big O notation and why it matters.", "How do you handle a disagreement with a teammate on a technical decision?", "Describe the difference between a REST API and GraphQL.", "How do you ensure your code is scalable and maintainable?", "Tell me about a time you had to learn a new technology quickly."],
    "Data Scientist": ["What is the difference between L1 and L2 regularization?", "How do you deal with outlier values in a dataset?", "Explain the Random Forest algorithm to a non-technical person.", "What metrics would you use to evaluate a classification model?", "Describe a data project where you had to present findings to stakeholders."],
    "Product Manager": ["How do you prioritize a product roadmap with limited resources?", "Tell me about a product you love and how you would improve it.", "How do you handle a situation where engineering and design disagree?", "What metrics would you use to measure the success of a new feature?", "Describe a time you had to pivot a product strategy based on data."],
    "UX Designer": ["Walk me through your design process from concept to prototype.", "How do you handle negative feedback on a design you're proud of?", "What is the difference between UI and UX?", "How do you ensure your designs are accessible to all users?", "Describe a time you used user research to solve a design problem."],
    "Marketing Analyst": ["Which KPIs are most important for a social media campaign?", "How do you calculate Customer Acquisition Cost (CAC)?", "Describe how you would perform an A/B test for an email campaign.", "How do you stay updated with the latest marketing trends?", "Explain how you use data to identify a target audience."]
}

def load_users():
    if not os.path.exists(USER_DB): return {}
    try:
        with open(USER_DB, 'r') as f: return json.load(f)
    except: return {}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        email = request.form.get('email')
        u = request.form.get('username')
        p = request.form.get('password') # Password visibility is handled by HTML input type
        if u in users: return "User exists!"
        users[u] = {"password": p, "email": email}
        with open(USER_DB, 'w') as f: json.dump(users, f)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        u, p = request.form.get('username'), request.form.get('password')
        if u in users and users[u]['password'] == p:
            session['user'] = u
            return redirect(url_for('index'))
        return "Invalid username or password"
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/api/questions/<role>')
def get_questions(role):
    return jsonify(ROLE_QUESTIONS.get(role, ["Tell me about yourself."]))

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    transcript = data.get('transcript', '').lower()
    words = re.findall(r'\b\w+\b', transcript)
    
    mistakes = []
    score = 4 

    # Technical depth keywords
    tech_keywords = ["algorithm", "complexity", "architecture", "database", "api", "framework", "performance", "deployment", "scalable", "star", "metrics", "kpi", "roi", "users"]
    
    found_tech = [w for w in words if w in tech_keywords]

    # Technical Analysis Feedback
    if len(found_tech) < 2:
        mistakes.append("Technical Depth: Try to include industry-specific terminology and architectural concepts.")
    else:
        score += 3

    if len(words) < 25:
        mistakes.append("Detail: Your answer is a bit brief. Use the STAR method to provide more context.")
    else:
        score += 2

    # Communication Check
    fillers = ['um', 'uh', 'ah', 'like', 'basically']
    filler_count = sum(1 for w in words if w in fillers)
    if filler_count > 3:
        mistakes.append(f"Clarity: High filler word count ({filler_count}). Try structured pauses instead.")
        score -= 1

    return jsonify({
        "score": max(1, min(10, score)), 
        "mistakes": list(set(mistakes)), # Unique mistakes only
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(debug=True)