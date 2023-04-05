import os
import flask
from flask import request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import random
from dotenv import load_dotenv, find_dotenv
from os import getenv
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)

import json

load_dotenv(find_dotenv())


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = "random string"
db = SQLAlchemy(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Person with username: {self.name}"


class Comments(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = rating = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    message = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self) -> str:
        return f"Person with username: {self.name}"


with app.app_context():
    db.create_all()

# Flask-login methods
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.form["info"]
        data = str(data)
        if data != "favicon.ico":
            user = Users.query.filter_by(name=data).first()
            if user:
                login_user(user)
                user = str(user.name)
                return redirect(url_for("home", user=user))
            else:
                return flask.render_template("wrong_login.html")

        # login check
    else:
        return flask.render_template("login.html")


@app.route("/", methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        data = request.form["info"]
        return redirect(url_for("register_user_to_db", username=data))
    else:
        return flask.render_template("register.html")
    # people = Person.query.all()
    # return repr(people)


@app.route("/<username>")
def register_user_to_db(username):
    if username != "favicon.ico":  # prevents from being added to db over and over
        user_table = Users(name=username)
        db.session.add(user_table)
        db.session.commit()
        # people = Person.query.all()
    return redirect(url_for("login"))


@app.route("/home/<user>")
@login_required
def home(user):
    # converts retrieved info into a string to be displayed easier
    genres = ""
    movie_id = ""
    movie_selection = random.randint(1, 9)
    if movie_selection <= 3:
        movie_id = "283566"
    elif movie_selection > 3 and movie_selection < 7:
        movie_id = "372058"
    else:
        movie_id = "533514"
    movies_list = get_movies_by__id(movie_id)
    poster_image = get_poster_image(movies_list["poster_path"])
    link = str(movies_list["title"])
    link = get_wiki_link(link)
    for i in range(len(movies_list["genres"])):
        if i == len(movies_list["genres"]) - 1:
            genres += (str(movies_list["genres"][i]["name"])) + ". "
        else:
            genres += (str(movies_list["genres"][i]["name"])) + ", "
    movie = movies_list
    # user = login_manager.user_loader
    return flask.render_template(
        "home.html",
        user=user,
        random_movie=movie,
        movie_genres=genres,
        poster=poster_image,
        wiki_link=link,
    )


# Uses id to acces IMDB database to retrieve stats
def get_movies_by__id(id):
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_MOVIES_PATH = "/movie/" + id

    movies_response = requests.get(
        TMDB_BASE_URL + TMDB_MOVIES_PATH,
        params={
            "api_key": getenv("TMDB_API_KEY"),
        },
    )
    movies_list = movies_response.json()
    return movies_list


def get_poster_image(path):
    TMDB_CONFIGURATION_URL = "https://api.themoviedb.org/3/configuration"

    config_response = requests.get(
        TMDB_CONFIGURATION_URL,
        params={
            "api_key": getenv("TMDB_API_KEY"),
        },
    )
    configuration_list = config_response.json()
    base_url = str(configuration_list["images"]["base_url"])
    poster_size = str(configuration_list["images"]["poster_sizes"][3])
    return base_url + poster_size + path


def get_wiki_link(movie_title):
    WIKI_BASE_URL = "https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&utf8=1&formatversion=2&srsearch="
    QUERY = movie_title
    CONFIGURATION = " movie"
    wiki_response = requests.get(WIKI_BASE_URL + QUERY)
    results = wiki_response.json()
    # gets top result page id to return it as a link
    results = str(results["query"]["search"][0]["pageid"])
    return "http://en.wikipedia.org/wiki?curid=" + results


app.run()
