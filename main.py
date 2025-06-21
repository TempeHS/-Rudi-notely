import re
from flask import Flask, render_template, request, redirect, flash, session, url_for
import userManagement as dbHandler

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a secure random key
#add different classes or groups to join
#Greenapple123@wda
#Joe_shmoe@12321
#add notifications 
@app.route("/")
def home():
    username = session.get('username')
    return render_template("index.html", username=username)

@app.route("/calender")
def calender():
    if 'username' not in session:
        return redirect(url_for("signin"))
    username = session['username']
    user_id = dbHandler.get_user_id(username)
    user_groups = dbHandler.get_user_groups(user_id)
    return render_template("calender.html", user_groups=user_groups)

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
    if 'username' not in session:
        return redirect(url_for("signin"))
    username = session['username']
    user_id = dbHandler.get_user_id(username)
    # Get group IDs the user is in
    user_groups = dbHandler.get_user_groups(user_id)
    group_ids = [g['id'] for g in user_groups]
    tasks = dbHandler.get_tasks_for_user_and_groups(user_id, group_ids)
    return render_template("homepage.html", username=username, tasks=tasks)


   

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

@app.route("/add_task", methods=["POST"])
def add_task():
    if 'username' not in session:
        return redirect(url_for("signin"))
    username = session['username']
    title = request.form.get("title")
    due_date = request.form.get("due_date")
    notes = request.form.get("notes")
    group_id = request.form.get("group_id") or None  # '' becomes None

    # Save the task, passing group_id (None for private)
    dbHandler.add_task(username, title, due_date, notes, group_id)
    flash("Task added!", "success")
    return redirect(url_for("homepage"))


# ...existing code...


@app.route("/groups", methods=["GET", "POST"])
def groups():
    if 'username' not in session:
        flash("Please sign in to access groups.", "danger")
        return redirect(url_for("signin"))
    username = session['username']
    user_id = dbHandler.get_user_id(username)
    user_groups = dbHandler.get_user_groups(user_id)
    selected_group_id = request.args.get("group_id")
    selected_group_members = None
    selected_group_name = None
    user_is_creator = False
    if selected_group_id:
        selected_group_members = dbHandler.get_group_members(selected_group_id)
        selected_group_name = dbHandler.get_group_name(selected_group_id)
        # Check if current user is creator
        for group in user_groups:
            if str(group["id"]) == str(selected_group_id):
                user_is_creator = dbHandler.is_user_creator(user_id, selected_group_id)
                break
    return render_template(
        "groups.html",
        user_groups=user_groups,
        selected_group_members=selected_group_members,
        selected_group_name=selected_group_name,
        selected_group_id=selected_group_id,
        user_is_creator=user_is_creator
    )

@app.route("/create_group", methods=["POST"])
def create_group():
    if 'username' not in session:
        return redirect(url_for("signin"))
    group_name = request.form.get("group_name")
    group_password = request.form.get("group_password")
    username = session['username']
    dbHandler.create_group(username, group_name, group_password)
    flash("Group created!", "success")
    return redirect(url_for("groups"))

@app.route("/join_group", methods=["POST"])
def join_group():
    if 'username' not in session:
        return redirect(url_for("signin"))
    group_name = request.form.get("group_name")
    group_password = request.form.get("group_password")
    username = session['username']
    if dbHandler.join_group(username, group_name, group_password):
        flash("Joined group!", "success")
    else:
        flash("Failed to join group. Check name/password.", "danger")
    return redirect(url_for("groups"))

@app.route("/edit_group", methods=["POST"])
def edit_group():
    if 'username' not in session:
        return redirect(url_for("signin"))
    group_id = request.form.get("group_id")
    new_group_name = request.form.get("new_group_name")
    new_group_password = request.form.get("new_group_password")
    username = session['username']
    user_id = dbHandler.get_user_id(username)
    if not dbHandler.is_user_creator(user_id, group_id):
        flash("Only the group creator can edit group details.", "danger")
        return redirect(url_for("groups", group_id=group_id))
    dbHandler.edit_group(username, group_id, new_group_name, new_group_password)
    flash("Group updated!", "success")
    return redirect(url_for("groups", group_id=group_id))

@app.route("/kick_member", methods=["POST"])
def kick_member():
    if 'username' not in session:
        return redirect(url_for("signin"))
    group_id = request.form.get("group_id")
    user_id = request.form.get("user_id")
    username = session['username']
    current_user_id = dbHandler.get_user_id(username)
    if not dbHandler.is_user_creator(current_user_id, group_id):
        flash("Only the group creator can kick members.", "danger")
        return redirect(url_for("groups", group_id=group_id))
    dbHandler.kick_member(username, group_id, user_id)
    flash("Member kicked!", "info")
    return redirect(url_for("groups", group_id=group_id))



@app.route("/delete_group", methods=["POST"])
def delete_group():
    if 'username' not in session:
        return redirect(url_for("signin"))
    group_id = request.form.get("group_id")
    username = session['username']
    if dbHandler.delete_group(username, group_id):
        flash("Group deleted.", "success")
    else:
        flash("You are not the creator of this group.", "danger")
    return redirect(url_for("groups"))

@app.route("/leave_group", methods=["POST"])
def leave_group():
    if 'username' not in session:
        return redirect(url_for("signin"))
    group_id = request.form.get("group_id")
    username = session['username']
    if dbHandler.leave_group(username, group_id):
        flash("You have left the group.", "info")
    else:
        flash("Group creators cannot leave their own group. Delete the group instead.", "danger")
    return redirect(url_for("groups"))


if __name__ == "__main__":
    app.run(debug=True)