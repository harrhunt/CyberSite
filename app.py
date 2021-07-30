from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import sass
import re
from flaskconf import SELECTED_CONFIG

sass.compile(dirname=('static/styles/sass', 'static/styles/css'), output_style='compressed')

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
    area_id = db.Column(db.Integer(), db.ForeignKey('areas.id', ondelete='CASCADE'), primary_key=True)
    unit_id = db.Column(db.Integer(), db.ForeignKey('units.id', ondelete='CASCADE'), primary_key=True)


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
    date_updated = db.Column(db.Date)
    description = db.Column(db.String(8192))
    notes = db.Column(db.String(8192))
    units = db.relationship('Unit', backref='modules', secondary='module_units')
    keywords = db.relationship('Keyword', backref='modules', secondary='module_keywords')
    files = db.relationship('File', backref='modules', secondary='module_files')
    links = db.relationship('Link', backref='modules', secondary='module_links')


class ModuleUnit(db.Model):
    __tablename__ = 'module_units'
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'), primary_key=True)
    unit_id = db.Column(db.Integer(), db.ForeignKey('units.id', ondelete='CASCADE'), primary_key=True)


class ModuleKeyword(db.Model):
    __tablename__ = 'module_keywords'
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'), primary_key=True)
    keyword_id = db.Column(db.Integer(), db.ForeignKey('keywords.id', ondelete='CASCADE'), primary_key=True)


class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    acronym = db.Column(db.String(30))


class ModuleFile(db.Model):
    __tablename__ = 'module_files'
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'), primary_key=True)
    file_id = db.Column(db.Integer(), db.ForeignKey('files.id', ondelete='CASCADE'), primary_key=True)


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), unique=True)
    date_added = db.Column(db.Date, default=date.today())


class ModuleLink(db.Model):
    __tablename__ = 'module_links'
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'), primary_key=True)
    link_id = db.Column(db.Integer(), db.ForeignKey('links.id', ondelete='CASCADE'), primary_key=True)


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(300), unique=True)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/module/<module_id>')
def module(module_id):
    selected_module = Module.query.filter(Module.id == module_id).first()
    if selected_module:
        return render_template("module.html", module=selected_module)


@app.route('/modules')
def modules():
    search_term = request.args.get('search')
    area_term = request.args.get('area')
    unit_term = request.args.get('unit')
    keyword_term = request.args.get('keyword')
    modules_left = Module.query.all()
    if area_term and area_term != '':
        modules_left = find_by_area(area_term, modules_left)
    if unit_term and unit_term != '':
        modules_left = find_by_unit(unit_term, modules_left)
    if keyword_term and keyword_term != '':
        modules_left = find_by_keyword(keyword_term, modules_left)
    if search_term and search_term != '':
        modules_left = find_by_search(search_term, modules_left)
    return render_template("modules.html", modules=modules_left)


def find_by_keyword(keyword_term, to_search):
    queried_modules = []
    for this_module in to_search:
        for keyword in this_module.keywords:
            if keyword.name == keyword_term:
                queried_modules.append(this_module)
    return queried_modules


def find_by_unit(unit_term, to_search):
    queried_modules = []
    for this_module in to_search:
        for unit in this_module.units:
            if unit.name == unit_term:
                queried_modules.append(this_module)
    return queried_modules


def find_by_area(area_term, to_search):
    queried_modules = []
    for this_module in to_search:
        for unit in this_module.units:
            for area in unit.areas:
                if area.name == area_term:
                    queried_modules.append(this_module)
    return queried_modules


def find_by_search(search_term, to_search):
    search = re.compile(f"\\b{search_term}\\b", re.IGNORECASE)
    queried_modules = []
    for this_module in to_search:
        print(len(this_module.keywords))
        if search.search(this_module.name) or search.search(this_module.author):
            queried_modules.append(this_module)
        else:
            found = False
            for keyword in this_module.keywords:
                if search.search(keyword.name) or search.search(keyword.acronym):
                    queried_modules.append(this_module)
                    found = True
                    break
            if found:
                continue
            for unit in this_module.units:
                if found:
                    break
                if search.search(unit.name):
                    queried_modules.append(this_module)
                    found = True
                    break
                else:
                    for area in unit.areas:
                        if search.search(area.name):
                            queried_modules.append(this_module)
                            found = True
                            break
    return queried_modules


if __name__ == '__main__':
    app.run()
