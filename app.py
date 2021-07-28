from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import sass
from flaskconf import SELECTED_CONFIG

sass.compile(dirname=('static/styles/sass', 'static/styles'), output_style='compressed')

app = Flask(__name__)
app.config.from_object(SELECTED_CONFIG)
db = SQLAlchemy(app)


class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    units = db.relationship('Unit', backref='areas', secondary='area_units')


class AreaUnit(db.Model):
    __tablename__ = 'area_units'
    id = db.Column(db.Integer(), primary_key=True)
    area_id = db.Column(db.Integer(), db.ForeignKey('areas.id', ondelete='CASCADE'))
    unit_id = db.Column(db.Integer(), db.ForeignKey('units.id', ondelete='CASCADE'))


class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)


class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    author = db.Column(db.String(100))
    date_added = db.Column(db.Date, default=date.today())
    description = db.Column(db.String(8192))
    notes = db.Column(db.String(8192))
    units = db.relationship('Unit', backref='modules', secondary='module_units')
    keywords = db.relationship('Keyword', backref='modules', secondary='module_keywords')
    files = db.relationship('File', backref='modules', secondary='module_files')
    links = db.relationship('Link', backref='modules', secondary='module_links')


class ModuleUnit(db.Model):
    __tablename__ = 'module_units'
    id = db.Column(db.Integer(), primary_key=True)
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'))
    unit_id = db.Column(db.Integer(), db.ForeignKey('units.id', ondelete='CASCADE'))


class ModuleKeyword(db.Model):
    __tablename__ = 'module_keywords'
    id = db.Column(db.Integer(), primary_key=True)
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'))
    keyword_id = db.Column(db.Integer(), db.ForeignKey('keywords.id', ondelete='CASCADE'))


class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    acronym = db.Column(db.String(30))


class ModuleFile(db.Model):
    __tablename__ = 'module_files'
    id = db.Column(db.Integer(), primary_key=True)
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'))
    file_id = db.Column(db.Integer(), db.ForeignKey('files.id', ondelete='CASCADE'))


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), unique=True)
    date_added = db.Column(db.Date, default=date.today())


class ModuleLink(db.Model):
    __tablename__ = 'module_links'
    id = db.Column(db.Integer(), primary_key=True)
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'))
    link_id = db.Column(db.Integer(), db.ForeignKey('links.id', ondelete='CASCADE'))


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(300), unique=True)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
