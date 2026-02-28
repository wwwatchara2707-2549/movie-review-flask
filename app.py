from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "movies.db")


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


@app.before_request
def initialize_database():
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
    search_query = request.args.get("search", "").strip()
    sort_option = request.args.get("sort", "")
    min_rating = request.args.get("min_rating")
    max_rating = request.args.get("max_rating")

    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    conn = get_db_connection()

    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    # ----- FILTER: MIN RATING -----
    if min_rating and min_rating.isdigit():
        query += " AND rating >= ?"
        params.append(int(min_rating))

    # ----- FILTER: MAX RATING -----
    if max_rating and max_rating.isdigit():
        query += " AND rating <= ?"
        params.append(int(max_rating))

    # ----- SEARCH -----
    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    # ----- SORT -----
    if sort_option == "high":
        query += " ORDER BY rating DESC"
    elif sort_option == "low":
        query += " ORDER BY rating ASC"
    else:
        query += " ORDER BY created_at DESC"

    # ----- PAGINATION -----
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    movies = conn.execute(query, params).fetchall()

    # ----- STATS (ใช้ filter เดียวกัน) -----
    count_query = "SELECT COUNT(*) FROM movies WHERE 1=1"
    count_params = []

    if min_rating and min_rating.isdigit():
        count_query += " AND rating >= ?"
        count_params.append(int(min_rating))

    if max_rating and max_rating.isdigit():
        count_query += " AND rating <= ?"
        count_params.append(int(max_rating))

    if search_query:
        count_query += " AND name LIKE ?"
        count_params.append(f"%{search_query}%")

    total_movies = conn.execute(count_query, count_params).fetchone()[0]

    avg_query = count_query.replace("COUNT(*)", "AVG(rating)")
    avg_result = conn.execute(avg_query, count_params).fetchone()[0]
    average_rating = round(avg_result, 2) if avg_result else 0

    highest_query = count_query.replace("COUNT(*)", "*") + " ORDER BY rating DESC LIMIT 1"
    highest_rated = conn.execute(highest_query, count_params).fetchone()

    total_pages = (total_movies + per_page - 1) // per_page

    conn.close()

    return render_template(
        "index.html",
        movies=movies,
        search_query=search_query,
        sort_option=sort_option,
        min_rating=min_rating,
        max_rating=max_rating,
        total_movies=total_movies,
        average_rating=average_rating,
        highest_rated=highest_rated,
        page=page,
        total_pages=total_pages
    )


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
# EDIT MOVIE
# ----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_movie(id):
    conn = get_db_connection()
    movie = conn.execute("SELECT * FROM movies WHERE id = ?", (id,)).fetchone()

    if movie is None:
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        review = request.form.get("review", "").strip()
        rating = request.form.get("rating", "")

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            flash("Rating must be between 1 and 5.", "error")
            conn.close()
            return redirect(url_for("edit_movie", id=id))

        conn.execute(
            """
            UPDATE movies
            SET name = ?, review = ?, rating = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (name, review, int(rating), id)
        )
        conn.commit()
        conn.close()

        flash("Movie updated successfully!", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", movie=movie)


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


# ----------------------------
# LOCAL RUN
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)