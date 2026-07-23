from flask import flask

app = Flask(__name__)

@app.route("/")
def index():
    return {"message": "Welcome to Codex Practice!"}

if __name__ == "__main__":
    app.run(debug=True)
