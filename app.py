import os
from flask import (
  Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
  import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/<username>")
def loggedin(username):
  username = mongo.db.Users.find_one(
    {"username": session["user"]})["username"]
  user = mongo.db.Users.find_one({"username": session["user"]})
  print(user)
  return render_template("index.html", username=username, user=user)


@app.route("/get_users")
def get_users():
  users = mongo.db.Users.find()
  print(users)
  return render_template("users.html", users=users)


@app.route("/login", methods=["GET", "POST"])
def login():
  """
  login page view, with two fileds, username, email,
  """
  if request.method == "POST":
      username = request.form.get("username")
      password = request.form.get("password")

      existing_user = mongo.db.Users.find_one(
          {"username": request.form.get("username")})

      if existing_user:
          # ensure hashed password matches user input
          if check_password_hash(existing_user["password"], password):
              session["user"] = username
              flash("Welcome, {}".format(
                  username))
              return redirect(url_for("loggedin", username=session["user"]))
          else:
              # invalid password match
              flash("Incorrect Username and/or Password")
              return redirect(url_for("login"))

      else:
          # username doesn't exist
          flash("Incorrect Username and/or Password")
          return redirect(url_for("login"))

  return render_template("login.html")


# logs out user
@app.route("/logout")
def logout():
    """
    This function allows a user to log out and removes them from
    the session cookie
    """
    # remove user from session cookies
    flash("Logged Out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    register page view, with four fileds, username, email,
    password, and confirm password
    """
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        email = request.form.get("email").lower()
        tel = request.form.get("tel")

        # *** check if username already exists in db
        existing_user = mongo.db.Users.find_one({"username": username})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        if password == confirm_password:
            register = {
                "username": username,
                "password": generate_password_hash(password),
                "email": email,
                "tel": tel,
            }
            mongo.db.Users.insert_one(register)

            # *** put the new user into 'session' cookie
            session["user"] = username
            flash("Registration Successful!")
            return redirect(url_for("loggedin", username=session["user"]))

        else:
            flash("Passwords do not match.")

    return render_template("register.html")


@app.route("/questionnaire/<username>", methods=["GET", "POST"])
def questionnaire(username):

  user = mongo.db.Users.find_one({"username": session["user"]})

  print(user)
  if request.method == "POST":
    answers = {
      "badges": request.form.getlist("questionnaire"),
      "highlights": request.form.get("highlights"),
      "extra": request.form.get("extra")
    }
    mongo.db.Users.update({"username": username}, {"$set": answers})
    return redirect(url_for("loggedin", username=session["user"]))
  
  tabs = mongo.db.Tabs.find().sort("name")
  
  return render_template("form.html", username=username, tabs=tabs)


@app.errorhandler(404)
def page_not_found(e):
    """
    give 404 error id the page do not exisit
    """
    return render_template('404.html'), 404


if __name__ == "__main__":
    """
    Runs app
    """
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG"))


