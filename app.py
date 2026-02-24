from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# เก็บข้อมูลชั่วคราวใน list (ยังไม่ใช้ database)
movies = []


# ----------------------------
# HOME PAGE + SEARCH
# ----------------------------
@app.route("/")
def index():
    search_query = request.args.get("search", "").lower()

    if search_query:
        filtered_movies = [
            movie for movie in movies
            if search_query in movie["name"].lower()
        ]
    else:
        filtered_movies = movies

    return render_template(
        "index.html",
        movies=filtered_movies,
        search_query=search_query
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
            return render_template(
                "add.html",
                error="Please fill all fields."
            )

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