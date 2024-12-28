from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import date

app = Flask(__name__)
DB_FILE = "db.sqlite3"

# Ensure database exists
if not os.path.exists(DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE UNIQUE NOT NULL,
                content TEXT NOT NULL
            )
        """)


@app.route("/", methods=["GET", "POST"])
def daily_entry():
    today = date.today().isoformat()
    if request.method == "POST":
        content = request.form.get("content", "")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO entries (entry_date, content) VALUES (?, ?)", (today, content))
            except sqlite3.IntegrityError:
                cursor.execute("UPDATE entries SET content = ? WHERE entry_date = ?", (content, today))
        return redirect(url_for("daily_entry"))
    
    # Retrieve today's entry if exists
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM entries WHERE entry_date = ?", (today,))
        entry = cursor.fetchone()
    return render_template("entry.html", entry=entry[0] if entry else "")


@app.route("/history")
def history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT entry_date, content FROM entries ORDER BY entry_date DESC")
        entries = cursor.fetchall()
    return render_template("history.html", entries=entries)


if __name__ == "__main__":
    app.run(debug=True)
