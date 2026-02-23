from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# เก็บรีวิวไว้ใน list ชั่วคราว (ยังไม่ใช้ database)
movies = []


@app.route("/")
def index():
    return render_template("index.html", movies=movies)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        name = request.form["name"].strip()
        review = request.form["review"].strip()
        rating = request.form["rating"]

        if name and review and rating:
            movies.append({
                "name": name,
                "review": review,
                "rating": rating
            })

        return redirect("/")

    return render_template("add.html")


@app.route("/delete/<int:index>", methods=["POST"])
def delete_movie(index):
    if 0 <= index < len(movies):
        movies.pop(index)
    return redirect("/")


@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_movie(index):
    if 0 <= index < len(movies):

        if request.method == "POST":
            name = request.form["name"].strip()
            review = request.form["review"].strip()
            rating = request.form["rating"]

            if not name or not review or not rating:
                error = "All fields are required!"
                return render_template(
                    "edit.html",
                    movie=movies[index],
                    error=error
                )

            movies[index] = {
                "name": name,
                "review": review,
                "rating": rating
            }

            return redirect("/")

        return render_template("edit.html", movie=movies[index])

    return redirect("/")