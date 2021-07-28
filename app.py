from datetime import date, datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from database import *
import sass
from flaskconf import SELECTED_CONFIG

sass.compile(dirname=('static/styles/sass', 'static/styles'), output_style='compressed')


app = Flask(__name__)
app.config.from_object(SELECTED_CONFIG)

db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
