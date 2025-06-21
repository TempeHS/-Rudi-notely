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



def add_task(username, title, due_date, notes, group_id=None):
    user_id = get_user_id(username)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (user_id, title, due_date, notes, group_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, due_date, notes, group_id)
        )
        conn.commit()

def get_tasks_for_user_and_groups(user_id, group_ids):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Private tasks
        query = """
            SELECT t.title, t.due_date, t.notes, u.username, NULL as group_name
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE t.user_id=? AND t.group_id IS NULL
        """
        params = [user_id]
        # Group tasks
        if group_ids:
            placeholders = ",".join("?" for _ in group_ids)
            query += f"""
                UNION
                SELECT t.title, t.due_date, t.notes, u.username, g.name as group_name
                FROM tasks t
                JOIN users u ON t.user_id = u.id
                JOIN groups g ON t.group_id = g.id
                WHERE t.group_id IN ({placeholders})
            """
            params += group_ids
        cur.execute(query, params)
        return [
            {
                "title": row[0],
                "due_date": row[1],
                "notes": row[2],
                "username": row[3],
                "group_name": row[4]
            }
            for row in cur.fetchall()
        ]




def get_user_id(username):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return row[0] if row else None

def get_user_groups(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT g.id, g.name
            FROM groups g
            JOIN user_groups ug ON g.id = ug.group_id
            WHERE ug.user_id = ?
        """, (user_id,))
        return [{"id": row[0], "name": row[1]} for row in cur.fetchall()]

def create_group(username, group_name, group_password):
    user_id = get_user_id(username)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO groups (name, password, creator_id) VALUES (?, ?, ?)",
            (group_name, group_password, user_id)
        )
        group_id = cur.lastrowid
        cur.execute(
            "INSERT INTO user_groups (user_id, group_id, is_creator) VALUES (?, ?, 1)",
            (user_id, group_id)
        )
        conn.commit()

def join_group(username, group_name, group_password):
    user_id = get_user_id(username)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM groups WHERE name = ?", (group_name,))
        row = cur.fetchone()
        if not row or row[1] != group_password:
            return False
        group_id = row[0]
        try:
            cur.execute("INSERT INTO user_groups (user_id, group_id, is_creator) VALUES (?, ?, 0)", (user_id, group_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def edit_group(username, group_id, new_group_name, new_group_password):
    user_id = get_user_id(username)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Only allow if user is creator
        cur.execute("SELECT is_creator FROM user_groups WHERE user_id=? AND group_id=?", (user_id, group_id))
        row = cur.fetchone()
        if not row or not row[0]:
            return False
        if new_group_name:
            cur.execute("UPDATE groups SET name=? WHERE id=?", (new_group_name, group_id)) 
        if new_group_password:
            cur.execute("UPDATE groups SET password=? WHERE id=?", (new_group_password, group_id))
        conn.commit()
        return True

def get_group_members(group_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.username, ug.is_creator
            FROM users u
            JOIN user_groups ug ON u.id = ug.user_id
            WHERE ug.group_id = ?
        """, (group_id,))
        return [{"id": row[0], "username": row[1], "is_creator": bool(row[2])} for row in cur.fetchall()]

def get_group_name(group_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM groups WHERE id = ?", (group_id,))
        row = cur.fetchone()
        return row[0] if row else None

def kick_member(username, group_id, user_id):
    # Only allow if current user is creator
    creator_id = get_user_id(username)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT is_creator FROM user_groups WHERE user_id=? AND group_id=?", (creator_id, group_id))
        row = cur.fetchone()
        if not row or not row[0]:
            return False
        # Don't allow kicking the creator
        cur.execute("SELECT is_creator FROM user_groups WHERE user_id=? AND group_id=?", (user_id, group_id))
        if cur.fetchone()[0]:
            return False
        cur.execute("DELETE FROM user_groups WHERE user_id=? AND group_id=?", (user_id, group_id))
        conn.commit()
        return True




def delete_group(username, group_id):
    user_id = get_user_id(username)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Check if user is the creator
        cur.execute("SELECT creator_id FROM groups WHERE id = ?", (group_id,))
        row = cur.fetchone()
        if not row or row[0] != user_id:
            return False
        # Delete from user_groups first (to avoid foreign key constraint)
        cur.execute("DELETE FROM user_groups WHERE group_id = ?", (group_id,))
        # Delete the group
        cur.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        conn.commit()
        return True


def is_user_creator(user_id, group_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT is_creator FROM user_groups WHERE user_id=? AND group_id=?", (user_id, group_id))
        row = cur.fetchone()
        return bool(row and row[0])

def leave_group(username, group_id):
    user_id = get_user_id(username)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Prevent creator from leaving their own group
        cur.execute("SELECT is_creator FROM user_groups WHERE user_id=? AND group_id=?", (user_id, group_id))
        row = cur.fetchone()
        if row and row[0]:
            return False  # Creator cannot leave
        cur.execute("DELETE FROM user_groups WHERE user_id=? AND group_id=?", (user_id, group_id))
        conn.commit()
        return True