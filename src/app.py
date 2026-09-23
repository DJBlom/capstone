import os

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    submitted_text = None
    if request.method == "POST":
        submitted_text = request.form.get("user_input", "")
    return render_template("index.html", submitted_text=submitted_text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
