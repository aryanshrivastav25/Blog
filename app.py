import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, location, delete_blog
import datetime

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///blog.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM user WHERE id = ?", user_id)
    username = data[0]["username"]

    blog_data = db.execute("SELECT * FROM blog")

    return render_template("index.html", username=username.capitalize(), blog_data=blog_data, datetime=datetime, len=len, check_user=username)


@app.route("/write", methods=["GET", "POST"])
@login_required
def write():
    """Write a blog"""
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM user WHERE id = ?", user_id)
    username = data[0]["username"]
    if request.method == "POST":
        blog = request.form.get("blog")
        if not blog:
            return apology("Please enter valid input")
        if len(blog) > 3000:
            return apology("Maximum word limit is 3000")
        db.execute("INSERT INTO blog (user_id, blog, username) VALUES(?, ?, ?)", user_id, blog, username)
        return redirect("/")
    return render_template("write.html", username=username.capitalize())


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("username")

        data = db.execute("SELECT * FROM user WHERE username = ?", username)
        check_password = data[0]["password"]
        if not check_password_hash(check_password, password) or len(data) != 1:
            return apology("Incorrect username and/or password")
        session["user_id"] = data[0]["id"]

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not username or not password or not confirm:
            return apology("Please enter username and/or password")
        elif confirm != password:
            return apology("Passwords do not match")

        data = db.execute("SELECT * FROM user")
        for i in range(len(data)):
            if data[i]["username"] == username:
                return apology("Username already exists")

        db.execute("INSERT INTO user (username, password) VALUES(?, ?)", username, generate_password_hash(password))
        return redirect("/")

    return render_template("register.html")


@app.route("/delete")
@login_required
def delete():
    blog_id = request.args.get("blog_id")
    db.execute("DELETE FROM blog WHERE blog_id = ?", blog_id)
    return redirect("/")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM user WHERE id = ?", user_id)
    username = data[0]["username"]
    if request.method == "GET":
        blog_id = request.args.get("blog_id")
        data = db.execute("SELECT * FROM blog WHERE blog_id = ?", blog_id)
        blog = data[0]["blog"]
        return render_template("edit.html", blog=blog, blog_id=blog_id, username=username.capitalize(), check_user=username)
    edit_blog = request.form.get("blog")
    blog_id = request.form.get("blog_id")
    db.execute("UPDATE blog SET blog = ? WHERE blog_id = ?", edit_blog, blog_id)
    return redirect("/")


@app.route("/your_blogs")
def view_blogs():
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM user WHERE id = ?", user_id)
    username = data[0]["username"]
    blog_data = db.execute("SELECT * FROM blog WHERE user_id = ?", user_id)
    return render_template("view_blogs.html", username=username.capitalize(), blog_data=blog_data, datetime=datetime, check_user=username)

@app.route("/account", methods=["GET", "POST"])
def account():
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM user WHERE id = ?", user_id)
    username = data[0]["username"]
    if request.method == "GET":
        return render_template("account.html", username=username.capitalize(), check_user=username)
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    check_password = data[0]["password"]

    if not check_password_hash(check_password, current_password):
        return apology("Incorrect current password")
    if not current_password or not new_password or not confirm_password:
        return apology("Please enter valid input")
    if new_password != confirm_password:
        return apology("Password do not match")
    db.execute("UPDATE user SET password = ? WHERE id = ?", generate_password_hash(new_password), user_id)
    return redirect("/")


@app.route("/search")
def search():
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM user WHERE id = ?", user_id)
    username = data[0]["username"]

    searched = request.args.get("search")
    if not search:
        return redirect("/")
    blog_data = db.execute("SELECT * FROM blog WHERE blog LIKE ?", "%" + searched + "%")
    if (len(blog_data)) == 0:
        return apology("No search results for your search")
    return render_template("search.html", blog_data=blog_data, username=username.capitalize(), check_user=username, searched=searched, datetime=datetime)