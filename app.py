import os
import flask
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import random
from dotenv import load_dotenv, find_dotenv
from os import getenv
import json

load_dotenv(find_dotenv())


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)


class Users(db.Model):
    name = db.Column(db.String(80), primary_key=True)

    def __repr__(self) -> str:
        return f"Person with username: {self.name}"


with app.app_context():
    db.create_all()


@app.route("/")
def login():
    return flask.render_template("login.html")
    # people = Person.query.all()
    # return repr(people)


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
    user_table = Users(name=username)
    db.session.add(user_table)
    db.session.commit()
    # people = Person.query.all()
    return redirect(url_for("login"))


@app.route("/home")
def home():
    # converts retrieved info into a string to be displayed easier
    genres = ""
    movie_selection = random.randint(1, 9)
    if movie_selection <= 3:
        movies_list = get_movies_by__id("283566")
    elif movie_selection > 3 and movie_selection < 7:
        movies_list = get_movies_by__id("372058")
    else:
        movies_list = get_movies_by__id("533514")
    poster_image = get_poster_image(movies_list["poster_path"])
    link = str(movies_list["title"])
    link = get_wiki_link(link)
    for i in range(len(movies_list["genres"])):
        if i == len(movies_list["genres"]) - 1:
            genres += (str(movies_list["genres"][i]["name"])) + ". "
        else:
            genres += (str(movies_list["genres"][i]["name"])) + ", "
    movie = movies_list

    return flask.render_template(
        "home.html",
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
