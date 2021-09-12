import os
from flask import (
  Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
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


@app.route("/get_users")
def get_users():
  users = mongo.db.Users.find()
  print(users)
  return render_template("users.html", users=users)


@app.route("/form")
def form():
  return render_template(
    'form.html'
  )


@app.route("/questionnaire/<user_id>", methods=["GET", "POST"])
def questionnaire(user_id):

  if request.method == "POST":
    answers = {
      "badges": request.form.getlist("questionnaire")
    }
    mongo.db.Users.update({"_id": ObjectId(user_id)}, {"$set": answers})
    return redirect(url_for("index"))
  
  tabs = mongo.db.Tabs.find().sort("name")
  
  return render_template("form.html", user_id=user_id, tabs=tabs)


if __name__ == "__main__":
    """
    Runs app
    """
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG"))


