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

        if name and review:
            movies.append({
                "name": name,
                "review": review
            })

        return redirect("/")

    return render_template("add.html")


# ✅ DELETE ROUTE (แก้ Method Not Allowed แล้ว)
@app.route("/delete/<int:index>", methods=["POST"])
def delete_movie(index):
    if 0 <= index < len(movies):
        movies.pop(index)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)