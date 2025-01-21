from flask import Flask, render_template
import os

app = Flask(
    __name__,
    template_folder="../Frontend/templates",  # Path to templates
    static_folder="../Frontend/static"        # Path to static files
)

@app.route("/")
def home():
    return render_template("index.html")  # Correct template path

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/bestiling")
def bestiling():
    return render_template("bestiling.html")

@app.route("/om_oss")
def om_oss():
    return render_template("om_oss.html")

@app.route("/tabel")
def tabel():
    return render_template("tabel.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)