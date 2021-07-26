from datetime import date, datetime

from flask import Flask, render_template
from flask_mongoalchemy import MongoAlchemy
from mongoalchemy.fields import StringField, IntField, DateTimeField, DocumentField, ListField, ObjectIdField
import sass
from credentials import *

sass.compile(dirname=('static/styles/sass', 'static/styles'), output_style='compressed')


class ConfigClass(object):
    MONGOALCHEMY_DATABASE = 'iicl'


app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config.from_object(f"{__name__}.ConfigClass")

db = MongoAlchemy(app)


class Area(db.Document):
    config_collection_name = 'areas'
    name = StringField()
    units = ListField(DocumentField('Unit'))


class Unit(db.Document):
    config_collection_name = 'units'
    name = StringField()
    area_id = ObjectIdField()


class Keyword(db.Document):
    config_collection_name = 'keywords'
    name = StringField()


class Module(db.Document):
    config_collection_name = 'modules'
    name = StringField()
    author = StringField()
    date_added = DateTimeField()
    description = StringField()
    notes = StringField()
    units = ListField(DocumentField('Unit'))
    files = ListField(DocumentField('File'))
    sources = ListField(DocumentField('Source'))
    keywords = ListField(DocumentField('Keyword'))


class File(db.Document):
    config_collection_name = 'files'
    name = StringField()
    date_added = DateTimeField()


class Source(db.Document):
    config_collection_name = 'sources'
    url = StringField()


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
