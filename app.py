from flask import Flask, render_template, request, redirect

app = Flask(__name__)

movies = []

@app.route("/")
def home():
    return render_template("index.html", movies=movies)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        name = request.form["name"].strip()
        review = request.form["review"].strip()

        if name and review:
            movies.append({
                "name": name,
                "review": review
            })

        return redirect("/")

    return render_template("add.html")


if __name__ == "__main__":
    app.run(debug=True)