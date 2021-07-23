from datetime import date, datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import sass
from credentials import *

sass.compile(dirname=('static/styles/sass', 'static/styles'), output_style='compressed')


class ConfigClass(object):
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config.from_object(f"{__name__}.ConfigClass")

db = SQLAlchemy(app)


class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))


class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))


class Keyword(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))


class Module(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    date_added = db.Column(db.Date, default=date.today())
    description = db.Column(db.String(8192))
    notes = db.Column(db.String(8192))


class File(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), unique=True)
    date_added = db.Column(db.Date, default=date.today())


class Source(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(300), unique=True)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
