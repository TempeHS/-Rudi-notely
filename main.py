import re
from flask import Flask, render_template, request, redirect, flash, session, url_for
import userManagement as dbHandler

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a secure random key

@app.route("/")
def home():
    username = session.get('username')
    return render_template("index.html", username=username)

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not validate_password(password):
            return render_template("signin.html")
        if dbHandler.signin(str(username), str(password)):
            session['username'] = username
            flash(f"User {username} signed in successfully!", 'success')
            # Redirect to homepage after successful sign in
            return redirect(url_for("homepage"))
        else:
            flash("Invalid username or password", 'danger')
            return render_template("signin.html")
    return render_template("signin.html")

@app.route("/homepage")
def homepage():
    username = session.get('username')
    return render_template("homepage.html", username=username)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        # Validate the password
        if not validate_password(password):
            return render_template("signup.html")
        if dbHandler.signup(str(username), str(email), str(password)):
            flash("Sign up successful!", "success")
            return redirect(url_for("signin"))
        else:
            flash("Username or email already exists.", "danger")
            return render_template("signup.html")
    return render_template("signup.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

def validate_password(password):
    if len(password) < 8:
        flash("Password must be at least 8 characters long", 'danger')
        return False
    if not re.search(r"[A-Z]", password):
        flash("Password must contain at least one uppercase letter", 'danger')
        return False
    if not re.search(r"[a-z]", password):
        flash("Password must contain at least one lowercase letter", 'danger')
        return False
    if not re.search(r"[0-9]", password):
        flash("Password must contain at least one number", 'danger')
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        flash("Password must contain at least one special character", 'danger')
        return False
    return True

if __name__ == "__main__":
    app.run(debug=True)