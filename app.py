from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "movies.db"


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
            rating INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


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
    filter_rating = request.args.get("min_rating", "")

    conn = get_db_connection()

    # Base query
    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    conn = get_db_connection()

    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    if filter_rating and filter_rating.isdigit():
        query += " AND rating >= ?"
        params.append(int(filter_rating))

    if sort_option == "high":
        query += " ORDER BY rating DESC"
    elif sort_option == "low":
        query += " ORDER BY rating ASC"

    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    movies = conn.execute(query, params).fetchall()

    # SEARCH
    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    # FILTER
    if filter_rating and filter_rating.isdigit():
        query += " AND rating >= ?"
        params.append(int(filter_rating))

    # SORT
    if sort_option == "high":
        query += " ORDER BY rating DESC"
    elif sort_option == "low":
        query += " ORDER BY rating ASC"

    movies = conn.execute(query, params).fetchall()

    # ---------- STATISTICS ----------
    total_movies = conn.execute(
        "SELECT COUNT(*) FROM movies"
    ).fetchone()[0]

    avg_result = conn.execute(
        "SELECT AVG(rating) FROM movies"
    ).fetchone()[0]

    average_rating = round(avg_result, 2) if avg_result else 0

    highest_rated = conn.execute(
        "SELECT * FROM movies ORDER BY rating DESC LIMIT 1"
    ).fetchone()

    total_count = conn.execute(
        "SELECT COUNT(*) FROM movies"
    ).fetchone()[0]

    total_pages = (total_count + per_page - 1) // per_page
    conn.close()

    return render_template(
    "index.html",
    movies=movies,
    search_query=search_query,
    sort_option=sort_option,
    filter_rating=filter_rating,
    total_movies=total_movies,
    average_rating=average_rating,
    highest_rated=highest_rated,   # ← ใส่ comma ตรงนี้
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
            return render_template("add.html", error="Please fill all fields.")

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            return render_template("add.html", error="Rating must be between 1 and 5.")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO movies (name, review, rating) VALUES (?, ?, ?)",
            (name, review, rating)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add.html", error=None)


# ----------------------------
# EDIT MOVIE
# ----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_movie(id):
    conn = get_db_connection()
    movie = conn.execute(
        "SELECT * FROM movies WHERE id = ?",
        (id,)
    ).fetchone()

    if movie is None:
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        review = request.form.get("review", "").strip()
        rating = request.form.get("rating", "")

        if not name or not review or not rating:
            conn.close()
            return render_template(
                "edit.html",
                movie=movie,
                error="Please fill all fields."
            )

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            conn.close()
            return render_template(
                "edit.html",
                movie=movie,
                error="Rating must be between 1 and 5."
            )

        conn.execute(
            "UPDATE movies SET name = ?, review = ?, rating = ? WHERE id = ?",
            (name, review, rating, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", movie=movie, error=None)


# ----------------------------
# DELETE MOVIE
# ----------------------------
@app.route("/delete/<int:id>", methods=["POST"])
def delete_movie(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM movies WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ----------------------------
# RUN SERVER
# ----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)