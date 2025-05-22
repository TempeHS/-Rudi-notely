import sqlite3

DB_PATH = "databasefiles/mydatabase.db"

def signup(username, email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def signin(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()
    return user is not None



def add_task(username, due_date, title, notes):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (username, due_date, title, notes) VALUES (?, ?, ?, ?)",
            (username, due_date, title, notes)
        )
        conn.commit()

def get_tasks_for_user(username):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT title, due_date, notes FROM tasks WHERE username = ? ORDER BY due_date ASC",
            (username,)
        )
        rows = cur.fetchall()
    # Return a list of dicts for easy use in Jinja templates
    return [
        {"title": row[0], "due_date": row[1], "notes": row[2]}
        for row in rows
    ]