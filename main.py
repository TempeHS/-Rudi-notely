#python main.py
#pip install -r requirements.txt
#http://127.0.0.1:5000


from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signin")
def signin():
    print("Sign In page accessed")  # Debug message
    return render_template("signin.html")

@app.route("/signup")
def signup():
    print("Sign Up page accessed")  # Debug message
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)

