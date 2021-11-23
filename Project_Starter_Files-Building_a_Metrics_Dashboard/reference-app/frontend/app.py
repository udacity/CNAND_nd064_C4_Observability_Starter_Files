from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()
