from flask import Flask, render_template, render_template_string, request, abort, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from zipfile import ZipFile, ZIP_DEFLATED
import sass
import re
import os
import io
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
    sources = db.relationship('Source', backref='keywords', secondary='keyword_sources')


class KeywordSource(db.Model):
    __tablename__ = 'keyword_sources'
    keyword_id = db.Column(db.Integer(), db.ForeignKey('keywords.id', ondelete='CASCADE'), primary_key=True)
    source_id = db.Column(db.Integer(), db.ForeignKey('sources.id', ondelete='CASCADE'), primary_key=True)


class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)


class ModuleFile(db.Model):
    __tablename__ = 'module_files'
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'), primary_key=True)
    file_id = db.Column(db.Integer(), db.ForeignKey('files.id', ondelete='CASCADE'), primary_key=True)


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200))
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
    else:
        return render_template_string("<h1>Module with id {{ module_id }} does not exist</h1>", module_id=module_id)


@app.route('/modules')
def modules():
    search_term = request.args.get('search')
    area_term = request.args.get('area')
    unit_term = request.args.get('unit')
    keyword_term = request.args.get('keyword')
    modules_left = Module.query.all()
    if not modules_left:
        return render_template("modules.html")
    if area_term and area_term != '':
        modules_left = find_by_area(area_term, modules_left)
    if unit_term and unit_term != '':
        modules_left = find_by_unit(unit_term, modules_left)
    if keyword_term and keyword_term != '':
        modules_left = find_by_keyword(keyword_term, modules_left)
    if search_term and search_term != '':
        modules_left = find_by_search(search_term, modules_left)
    return render_template("modules.html", modules=modules_left)


@app.route('/contribute')
def contribute():
    return render_template("contribute.html")


@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('file')
    to_save = []
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        if filename != '':
            ext = os.path.splitext(filename)[1]
            if not len(app.config["EXTENSIONS_WHITELIST"]):
                if ext in app.config["EXTENSIONS_BLACKLIST"]:
                    return 'This type of file is  not allowed', 400
            else:
                if ext not in app.config["EXTENSIONS_WHITELIST"]:
                    return 'This type of file is  not allowed', 400
            new_file = File(name=filename)
            db.session.add(new_file)
            to_save.append((file, new_file))
        else:
            return '', 204
    db.session.commit()
    for file in to_save:
        file[0].save(os.path.join(app.config["UPLOAD_PATH"], str(file[1].id)))
    return '', 200


@app.route('/download/<file_id>')
def download(file_id):
    file_to_download = File.query.filter(File.id == file_id).first()
    if not file_to_download:
        abort(404)
    return send_from_directory(app.config["UPLOAD_PATH"], str(file_to_download.id), as_attachment=True, download_name=file_to_download.name)


@app.route('/download_all/<module_id>')
def download_all(module_id):
    module_to_zip = Module.query.filter(Module.id == module_id).first()
    if not module_to_zip:
        abort(404)
    files_to_zip = module_to_zip.files
    zip_bytes = io.BytesIO()
    with ZipFile(zip_bytes, "a", ZIP_DEFLATED, True) as zip_file:
        for file in files_to_zip:
            with open(os.path.join(app.config["UPLOAD_PATH"], str(file.id)), 'rb') as fp:
                zip_file.writestr(file.name, fp.read())
    zip_bytes.seek(0)
    return send_file(zip_bytes, as_attachment=True, download_name=f"{module_to_zip.name.replace(' ', '_')}.zip")


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
