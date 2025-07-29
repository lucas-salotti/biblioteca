from flask import Flask, redirect, url_for, render_template, request, session, flash
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from datetime import timedelta
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy

ROOT_PATH = Path(__file__).parent
app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


#TODO: Add is_operator and password to the db. Also, try to encrypt password.

class Users(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key = True)
    name: Mapped[str] = mapped_column(db.String(100))
    email: Mapped[str] = mapped_column(db.String(100), unique = True)
    
    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route("/")
def home():
    return render_template("index.html", content=["tim", "joe", "bill"], r=2)


#FIXME: fix the login function as it is not working anymore. Create a signup function as well.
@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST" and "nm" in request.form:
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        
        found_user =  Users.query.filter_by(name=user).first()
        
        if found_user:
            session["email"] = found_user.email

        else:
            usr = Users(user, "")
            db.session.add(usr)
            db.session.commit()

        flash("Login Successful!")
        return redirect(url_for("user"))
     
    
    elif request.method =="POST" and "dobada" in request.form:
        return f"<h1>Merely a placeholder"
    
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("user")) 
        return render_template("login.html")


# TODO: Make it so you can insert lots of IDs, emails, names to see/delete at once, separated by comma.
@app.route("/view", methods=["GET", "POST", "DELETE"])
def view():

    if request.method == "GET":
        return render_template("view.html", values=Users.query.all())
    
    elif request.method == "POST":
        user_type = request.form["deleteUserType"]
        user = request.form["deleteUserInfo"]
        data = {user_type: user}
        
        found_user = Users.query.filter_by(**data).first()

        if found_user:
            db.session.delete(found_user)
            db.session.commit()

        else:
            flash("No user found with inserted parameters.")

        return render_template("view.html", values=Users.query.all())

# TODO: Add admin page and make it verifiable by database.
def verify():
        user = request.form["nm"]
        usr = Users.query.filter_by(nome=user).first()
        print(usr)
        if usr == None or usr.email != "gui@gmail.com":
            return redirect(url_for("admin"))
        
        session["user"] = usr.nome
        return redirect(url_for("user"))

@app.route("/user", methods=["POST", "GET"])
def user():

    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user =  Users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved")

        else:
            if "email" in session:
                email = session["email"]
        

        return render_template("user.html", email=email)
    
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out.")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin():
    pass


if __name__ == "__main__":
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True)