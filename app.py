from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ใช้ path แบบ fix สำหรับ Render
DATABASE = "/opt/render/project/src/movies.db"

# ----------------------------
# DATABASE SETUP
# ----------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            review TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# เรียกสร้าง DB ทันทีตอนแอพเริ่ม
init_db()


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def index():
    conn = get_db_connection()

    movies = conn.execute(
        "SELECT * FROM movies ORDER BY created_at DESC"
    ).fetchall()

    conn.close()

    return render_template("index.html", movies=movies)


# ----------------------------
# ADD MOVIE
# ----------------------------
@app.route("/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        review = request.form.get("review", "").strip()
        rating = request.form.get("rating", "")

        if not name or not review or not rating:
            flash("Please fill all fields.", "error")
            return redirect(url_for("add_movie"))

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            flash("Rating must be between 1 and 5.", "error")
            return redirect(url_for("add_movie"))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO movies (name, review, rating) VALUES (?, ?, ?)",
            (name, review, int(rating))
        )
        conn.commit()
        conn.close()

        flash("Movie added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


# ----------------------------
# DELETE MOVIE
# ----------------------------
@app.route("/delete/<int:id>", methods=["POST"])
def delete_movie(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM movies WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Movie deleted successfully!", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)