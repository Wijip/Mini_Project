from crypt import methods

from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "supersecretkey"

users ={}
tweets = []

@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html", tweets=tweets, users=session["user"])
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "❌ Username atau password salah"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username not in users:
            users[username] = password
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "❌ Username sudah digunakan!"
    return render_template("signup.html")

@app.route("/tweet", methods=["GET", "POST"])
def tweet():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form["content"]
        tweets.append({"user":session["user"], "content": content})
        return redirect(url_for("home"))
    return render_template("tweet.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)