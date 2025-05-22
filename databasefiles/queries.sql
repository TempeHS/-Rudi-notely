CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    due_date TEXT NOT NULL,
    title TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (username) REFERENCES users(username)
);