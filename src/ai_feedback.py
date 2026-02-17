def generate_feedback(confidence, fillers):
    feedback = []

    if confidence >= 80:
        feedback.append("Excellent confidence and clarity 👏")
    elif confidence >= 60:
        feedback.append("Good confidence, but can improve delivery 👍")
    else:
        feedback.append("Low confidence detected, needs more practice 😟")

    if fillers == 0:
        feedback.append("No filler words used – great fluency!")
    elif fillers <= 3:
        feedback.append("Few filler words – try to reduce them further.")
    else:
        feedback.append("Too many filler words – pause and think before speaking.")

    return feedback
