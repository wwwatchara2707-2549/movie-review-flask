from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# เก็บข้อมูลชั่วคราวใน list (ยังไม่ใช้ database)
movies = []


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def index():
    search_query = request.args.get("search", "").strip()
    sort_option = request.args.get("sort", "")
    filter_rating = request.args.get("min_rating", "")

    filtered_movies = movies

    # SEARCH
    if search_query:
        filtered_movies = [
            movie for movie in filtered_movies
            if search_query.lower() in movie["name"].lower()
        ]

    # FILTER BY MIN RATING
    if filter_rating and filter_rating.isdigit():
        filtered_movies = [
            movie for movie in filtered_movies
            if int(movie["rating"]) >= int(filter_rating)
        ]

    # SORT
    if sort_option == "high":
        filtered_movies = sorted(
            filtered_movies,
            key=lambda x: int(x["rating"]),
            reverse=True
        )
    elif sort_option == "low":
        filtered_movies = sorted(
            filtered_movies,
            key=lambda x: int(x["rating"])
        )

    total_movies = len(movies)

    if movies:
        average_rating = round(
            sum(int(m["rating"]) for m in movies) / total_movies,
            2
        )
        highest_rated = max(movies, key=lambda x: int(x["rating"]))
    else:
        average_rating = 0
        highest_rated = None

    return render_template(
        "index.html",
        movies=filtered_movies,
        search_query=search_query,
        sort_option=sort_option,
        filter_rating=filter_rating,
        total_movies=total_movies,
        average_rating=average_rating,
        highest_rated=highest_rated
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

        movies.append({
            "name": name,
            "review": review,
            "rating": rating
        })

        return redirect(url_for("index"))

    return render_template("add.html", error=None)


# ----------------------------
# EDIT MOVIE
# ----------------------------
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_movie(index):
    if 0 <= index < len(movies):

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            review = request.form.get("review", "").strip()
            rating = request.form.get("rating", "")

            if not name or not review or not rating:
                return render_template(
                    "edit.html",
                    movie=movies[index],
                    error="Please fill all fields."
                )

            if not rating.isdigit() or not (1 <= int(rating) <= 5):
                return render_template(
                    "edit.html",
                    movie=movies[index],
                    error="Rating must be between 1 and 5."
                )

            movies[index] = {
                "name": name,
                "review": review,
                "rating": rating
            }

            return redirect(url_for("index"))

        return render_template("edit.html", movie=movies[index], error=None)

    return redirect(url_for("index"))


# ----------------------------
# DELETE MOVIE
# ----------------------------
@app.route("/delete/<int:index>", methods=["POST"])
def delete_movie(index):
    if 0 <= index < len(movies):
        movies.pop(index)
    return redirect(url_for("index"))


# ----------------------------
# RUN SERVER
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)