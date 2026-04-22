let questions = [], currentIdx = 0, scores = [], allMistakes = [];
let stream = null;
let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

recognition.continuous = true;
recognition.interimResults = true;
let finalTranscript = ""; 

async function startSession() {
    const role = document.getElementById('roleSelect').value;
    if(!role) return;
    const res = await fetch(`/api/questions/${role}`);
    questions = await res.json();
    currentIdx = 0; scores = []; allMistakes = [];
    loadQuestion();
}

function loadQuestion() {
    document.getElementById('qText').innerText = `Question ${currentIdx + 1}: ${questions[currentIdx]}`;
    document.getElementById('nextBtn').style.display = "none";
    document.getElementById('recBtn').style.display = "inline-block";
    document.getElementById('recBtn').disabled = false;
    document.getElementById('recBtn').classList.remove('btn-stop-active');
    
    // FIX: Ensure Microphone Icon is visible
    document.getElementById('recBtn').innerHTML = "🎤 Start Recording";
    document.getElementById('recBtn').onclick = startRecording; 
    
    document.getElementById('transcript').innerText = "Waiting for speech...";
    finalTranscript = ""; // Reset transcript for new question
}

function startRecording() {
    finalTranscript = ""; 
    try {
        recognition.start();
        document.getElementById('recBtn').innerHTML = "🛑 Stop & Submit";
        document.getElementById('recBtn').classList.add('btn-stop-active');
        document.getElementById('recBtn').onclick = stopRecording;
    } catch (e) { console.error("Mic already active", e); }
}

function stopRecording() {
    recognition.stop();
    document.getElementById('recBtn').innerText = "Analyzing...";
    document.getElementById('recBtn').disabled = true;

    // Wait 1 second for the final speech chunk to settle
    setTimeout(() => {
        if (!finalTranscript || finalTranscript.trim().length < 5) {
            alert("Speak Louder! We couldn't catch that answer.");
            loadQuestion();
        } else {
            analyzeSpeech(finalTranscript);
        }
    }, 1000);
}

recognition.onresult = (event) => {
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
        else interim += event.results[i][0].transcript;
    }
    document.getElementById('transcript').innerText = finalTranscript + interim;
};

async function analyzeSpeech(text) {
    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ transcript: text })
        });
        const data = await res.json();
        
        scores.push(data.score);
        if(data.mistakes) allMistakes.push(...data.mistakes);
        
        document.getElementById('recBtn').style.display = "none";
        document.getElementById('nextBtn').style.display = "inline-block";
    } catch (err) {
        console.error("Analysis Error:", err);
        loadQuestion();
    }
}

function goToNext() {
    if (currentIdx < 4) {
        currentIdx++;
        loadQuestion();
    } else {
        // AUTOMATIC REDIRECT logic
        alert("🎉 Interview Completed! Redirecting to your Performance Dashboard.");
        finishInterview();
    }
}

function finishInterview() {
    // 1. Switch to progress tab automatically
    switchTab('progress');

    // 2. Calculate and Display Scores
    if(scores.length > 0) {
        const sum = scores.reduce((a, b) => a + b, 0);
        const avg = (sum / scores.length).toFixed(1);
        document.getElementById('finalScore').innerText = avg;
        document.getElementById('finalStatus').innerText = avg >= 7 ? "Strong Hire" : "Keep Practicing";
    }

    // 3. Display Technical Feedback
    const list = document.getElementById('mistakesList');
    list.innerHTML = "";
    if (allMistakes.length === 0) {
        list.innerHTML = "<li>Technical delivery was excellent and detailed.</li>";
    } else {
        [...new Set(allMistakes)].forEach(m => {
            let li = document.createElement('li');
            li.innerText = m;
            list.appendChild(li);
        });
    }

    // 4. Render Chart
    const ctx = document.getElementById('perfChart').getContext('2d');
    if (window.myChart) { window.myChart.destroy(); }
    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Q1", "Q2", "Q3", "Q4", "Q5"],
            datasets: [{
                label: 'Confidence Score',
                data: scores,
                borderColor: '#6c63ff',
                backgroundColor: 'rgba(108, 99, 255, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function switchTab(tab) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tab + '-section').classList.add('active');
    document.getElementById(tab + '-tab').classList.add('active');
}

// FIXED WEBCAM LOGIC
async function toggleCam() {
    const v = document.getElementById('webcam');
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
        v.style.display = "none";
    } else {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            v.srcObject = stream;
            v.style.display = "block";
            v.play(); // Ensure camera starts playing immediately
        } catch (e) {
            alert("Please allow camera access in your browser settings.");
        }
    }
}