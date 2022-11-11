import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helper_functions import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///timetable.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of tasks"""
    study_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "study")
    others_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "others")
    deadlines_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "deadlines")
    if (study_table != [] or deadlines_table != []) and (others_table != [] or deadlines_table != []):
        if request.method == "POST":
            if 'DelTask_button' in request.form:
                task = request.form.get("task")
                date = request.form.get("date")
                if len(task) != 0  and date:
                    db.execute("""DELETE FROM study WHERE task = ? AND date = ? AND user_id = ?""", request.form.get("task"), request.form.get("date"), session.get("user_id"))
                    db.execute("""DELETE FROM others WHERE task = ? AND date = ? AND user_id = ?""", request.form.get("task"), request.form.get("date"), session.get("user_id"))
                    flash("Deleted!")
            else:
                db.execute("""DELETE FROM deadlines WHERE task = ? AND date = ? AND user_id = ?""", request.form.get("deadline"), request.form.get("date"), session.get("user_id"))
                flash("Deleted!")
        todays_tasks = db.execute("""SELECT * FROM study WHERE date = date() AND user_id = ? UNION ALL SELECT * FROM others WHERE date = date() AND user_id = ?""", session.get("user_id"), session.get("user_id"))
        deadlines = db.execute("""SELECT * FROM deadlines WHERE user_id = ? AND date BETWEEN DATE(date(), '-0 days') AND DATE(date(), '+10 days')""", session.get("user_id"))
        return render_template("index.html", todays_tasks=todays_tasks, deadlines=deadlines )
            
    else:
        return apology("No database found", 403)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        study_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "study")
        others_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "others")
        deadlines_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "deadlines")
        if (study_table != [] or deadlines_table != []) and (others_table != [] or deadlines_table != []):
            todays_tasks = db.execute("""SELECT * FROM study WHERE date = date() AND user_id = ? UNION ALL SELECT * FROM others WHERE date = date() AND user_id = ?""", session.get("user_id"), session.get("user_id"))
            deadlines = db.execute("""SELECT * FROM deadlines WHERE user_id = ? AND date BETWEEN DATE(date(), '-0 days') AND DATE(date(), '+10 days')""", session.get("user_id"))
            return render_template("index.html", todays_tasks=todays_tasks, deadlines=deadlines )
        else:
            return apology("No database found", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
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

        # Ensure username was submitted
        username = request.form.get("username")
        if not request.form.get("username"):
            return apology("Must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password", 400)

        if not request.form.get("confirmation"):
            return apology("Must confirm password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Provide same password in Confirm Password block", 400)

        #  database for username
        Registerants = db.execute("SELECT * FROM users")
        for registerant in Registerants:
            if username == registerant["username"]:
                return apology("Username already exists", 400)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))
        flash("Registered!")
        return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/study.html", methods=["GET", "POST"])
@login_required
def study():
    if request.method == "POST":
        if 'Add_button' in request.form:
            task = request.form.get("task")
            date = request.form.get("date")
            if len(task) != 0  and date:
                db.execute("INSERT INTO study (user_id, task, date) VALUES(?, ?, ?)", session.get("user_id"), task, date)
                flash("Added!")
                tasks = db.execute("""SELECT * FROM study WHERE date >= date() AND user_id = ? ORDER BY date""", session.get("user_id")) 
            else:
                return apology("Wrong Input, Click on the Study link to go back to the study page", 400)
        else:
            db.execute("""DELETE FROM study WHERE task = ? AND date = ? AND user_id = ?""", request.form.get("task"), request.form.get("date"), session.get("user_id"))
            flash("Deleted!")
            tasks = db.execute("""SELECT * FROM study WHERE date >= date() AND user_id = ? ORDER BY date""", session.get("user_id"))
    else:
        """Show portfolio of tasks"""
        study_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "study")
        if (study_table != []):
            tasks = db.execute("""SELECT * FROM study WHERE date >= date() AND user_id = ? ORDER BY date""", session.get("user_id"))
        else:
            return apology("No database Found", 400)
    return render_template("study.html", tasks=tasks)

@app.route("/grocery.html", methods=["GET", "POST"])
@login_required
def grocery():
    if request.method == "POST":
        if 'Add_button' in request.form:
            item = request.form.get("action")
            if len(item) != 0:
                db.execute("INSERT INTO groceryList (user_id, item) VALUES(?, ?)", session.get("user_id"), item)
                flash("Added!")
                items = db.execute("""SELECT * FROM groceryList WHERE user_id = ?""", session.get("user_id"))
            else:
                return apology("Wrong Input, Click on the Grocery link to go back to the grocery page", 400)
        else:
            db.execute("""DELETE FROM groceryList WHERE item = ? AND user_id = ?""", request.form.get("del_item"), session.get("user_id"))
            flash("Deleted!")
            items = db.execute("""SELECT * FROM groceryList WHERE user_id = ?""", session.get("user_id"))
    else:
        """Show portfolio of items"""
        grocery_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "groceryList")
        if (grocery_table != []):
            items = db.execute("""SELECT * FROM groceryList WHERE user_id = ?""", session.get("user_id"))
        else:
            return apology("No database Found", 400)
    return render_template("grocery.html", items=items)


@app.route("/deadlines.html", methods=["GET", "POST"])
@login_required
def deadlines():
    if request.method == "POST":
        if 'Add_button' in request.form:
            task = request.form.get("deadline")
            date = request.form.get("date")
            if len(task) != 0  and date:
                db.execute("INSERT INTO deadlines (user_id, task, date) VALUES(?, ?, ?)", session.get("user_id"), task, date)
                flash("Added!")
                deadlines = db.execute("""SELECT * FROM deadlines WHERE user_id = ? ORDER BY date""", session.get("user_id"))
            else:
                return apology("Wrong Input, Click on the Deadlines link to go back to the deadlines page", 400)
        else:
            db.execute("""DELETE FROM deadlines WHERE task = ? AND date = ? AND user_id = ?""", request.form.get("deadline"), request.form.get("date"), session.get("user_id"))
            flash("Deleted!")
            deadlines = db.execute("""SELECT * FROM deadlines WHERE user_id = ? ORDER BY date""", session.get("user_id"))
    else:
        """Show portfolio of deadlines"""
        deadlines_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "deadlines")
        if (deadlines_table != []):
            db.execute("DELETE FROM deadlines WHERE date < date() AND user_id = ?", session.get("user_id"))
            deadlines = db.execute("""SELECT * FROM deadlines WHERE user_id = ? ORDER BY date""", session.get("user_id"))
        else:
            return apology("No database Found", 400)
    return render_template("deadlines.html", deadlines=deadlines) 

@app.route("/others.html", methods=["GET", "POST"])
@login_required
def others():
    if request.method == "POST":
        if 'Add_button' in request.form:
            task = request.form.get("task")
            date = request.form.get("date")
            if len(task) != 0  and date:
                db.execute("INSERT INTO others (user_id, task, date) VALUES(?, ?, ?)", session.get("user_id"), task, date)
                flash("Added!")
                tasks = db.execute("""SELECT * FROM others WHERE user_id = ? ORDER BY date""", session.get("user_id"))
            else:
                return apology("Wrong Input, Click on the Others link to go back to the deadlines page", 400)
        else:
            db.execute("""DELETE FROM others WHERE task = ? AND date = ? AND user_id = ?""", request.form.get("task"), request.form.get("date"), session.get("user_id"))
            flash("Deleted!")
            tasks = db.execute("""SELECT * FROM others WHERE user_id = ? ORDER BY date""", session.get("user_id"))
    else:
        """Show portfolio of miscellaneous tasks"""
        others_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "others")
        if (others_table != []):
            db.execute("DELETE FROM others WHERE date < date() AND user_id = ?", session.get("user_id"))
            tasks = db.execute("""SELECT * FROM others WHERE user_id = ? ORDER BY date""", session.get("user_id"))
        else:
            return apology("No database Found", 400)
    return render_template("others.html", tasks=tasks)

@app.route("/pending.html", methods=["GET", "POST"])
@login_required
def pending():
    if request.method == "POST":

            db.execute("""DELETE FROM study WHERE task = ? AND date = ? AND user_id = ?""", request.form.get("task"), request.form.get("date"), session.get("user_id"))
            flash("Deleted!")
            tasks = db.execute("""SELECT * FROM study WHERE user_id = ? ORDER BY date""", session.get("user_id"))
    else:
        """Show portfolio of pending tasks"""
        pending_table = db.execute("""SELECT name FROM sqlite_master WHERE type = ? AND name = ?""", "table", "study")
        if (pending_table != []):
            tasks = db.execute("""SELECT * FROM study WHERE user_id = ? AND date < date()""", session.get("user_id"))
        else:
            return apology("No database Found", 400)
    return render_template("pending.html", tasks=tasks)