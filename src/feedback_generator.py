def generate_feedback(confidence, filler_count, speech_rate):
    feedback = []

    if confidence == "Low":
        feedback.append("Work on maintaining confidence and clarity while speaking.")
    elif confidence == "Medium":
        feedback.append("Good performance, but further improvement is possible.")
    else:
        feedback.append("Excellent confidence and communication skills.")

    if filler_count > 3:
        feedback.append("Reduce usage of filler words such as um, uh, and like.")

    if speech_rate < 3:
        feedback.append("Try speaking a bit faster to sound more confident.")
    elif speech_rate > 5:
        feedback.append("Try slowing down your speech for better clarity.")

    return feedback
