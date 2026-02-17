from database import get_connection

def save_interview(username, transcript, confidence, fillers):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO interviews (username, transcript, confidence, fillers) VALUES (?, ?, ?, ?)",
        (username, transcript, confidence, fillers)
    )

    conn.commit()
    conn.close()

def get_interviews(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT transcript, confidence, fillers FROM interviews WHERE username=?",
        (username,)
    )

    rows = cur.fetchall()
    conn.close()
    return rows
