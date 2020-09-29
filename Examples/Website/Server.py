# importing flask framework to make a server
from flask import Flask, render_template

app = Flask(__name__)  # initializing flask


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
