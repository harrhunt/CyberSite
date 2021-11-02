import sqlalchemy.exc
from flask import Flask, render_template, render_template_string, request, abort, send_from_directory, send_file, \
    redirect, url_for, flash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import date, datetime
from zipfile import ZipFile, ZIP_DEFLATED
import json
import sass
import os
import io
from flaskconf import SELECTED_CONFIG

sass.compile(dirname=('static/styles/sass', 'static/styles/css'), output_style='compressed')

app = Flask(__name__)
app.config.from_object(SELECTED_CONFIG)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User,
            'Area': Area,
            'Unit': Unit,
            'Module': Module,
            'Keyword': Keyword,
            'Source': Source,
            'File': File,
            'Link': Link
            }


@app.cli.command('initdb')
def initialize_database():
    db.create_all()
    new_admin = User.query.filter(User.username == 'admin').first()
    areas = Area.query.all()
    keywords = Keyword.query.all()
    if not new_admin:
        new_admin = User(username=app.config["ADMIN_USERNAME"],
                         password=generate_password_hash(app.config["ADMIN_PASSWORD"]))
        db.session.add(new_admin)
        db.session.commit()
    if not len(areas):
        load_areas()
    if not len(keywords):
        load_keywords()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(24), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(80))


class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    units = db.relationship(
        'Unit',
        backref='area',
        lazy='dynamic'
    )


class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    area_id = db.Column(db.Integer(), db.ForeignKey('areas.id', ondelete='CASCADE'))


class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    author = db.Column(db.String(100))
    date_added = db.Column(db.Date, default=date.today())
    date_updated = db.Column(db.Date)
    description = db.Column(db.String(8192))
    notes = db.Column(db.String(8192))
    units = db.relationship(
        'Unit',
        backref=db.backref('modules', lazy='dynamic'),
        secondary='module_units',
        lazy='dynamic'
    )
    keywords = db.relationship(
        'Keyword',
        backref=db.backref('modules', lazy='dynamic'),
        secondary='module_keywords',
        lazy='dynamic'
    )
    files = db.relationship(
        'File',
        backref='module',
        cascade='all, delete-orphan'
    )
    links = db.relationship(
        'Link',
        backref=db.backref('modules', lazy='dynamic'),
        secondary='module_links',
        lazy='dynamic'
    )


module_units = db.Table('module_units',
                        db.Column('module_id', db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'),
                                  primary_key=True),
                        db.Column('unit_id', db.Integer(), db.ForeignKey('units.id', ondelete='CASCADE'),
                                  primary_key=True)
                        )

module_keywords = db.Table('module_keywords',
                           db.Column('module_id', db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'),
                                     primary_key=True),
                           db.Column('keyword_id', db.Integer(), db.ForeignKey('keywords.id', ondelete='CASCADE'),
                                     primary_key=True)
                           )

module_links = db.Table('module_links',
                        db.Column('module_id', db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'),
                                  primary_key=True),
                        db.Column('link_id', db.Integer(), db.ForeignKey('links.id', ondelete='CASCADE'),
                                  primary_key=True)
                        )


class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    acronym = db.Column(db.String(30))
    sources = db.relationship(
        'Source',
        backref=db.backref('keywords', lazy='dynamic'),
        secondary='keyword_sources',
        lazy='dynamic'
    )


keyword_sources = db.Table('keyword_sources',
                           db.Column('keyword_id', db.Integer(), db.ForeignKey('keywords.id', ondelete='CASCADE'),
                                     primary_key=True),
                           db.Column('source_id', db.Integer(), db.ForeignKey('sources.id', ondelete='CASCADE'),
                                     primary_key=True)
                           )


class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200))
    date_added = db.Column(db.Date, default=date.today())
    module_id = db.Column(db.Integer(), db.ForeignKey('modules.id', ondelete='CASCADE'))


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(300), unique=True)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=24)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template("admin/login.html", form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter(User.username == form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_loc = request.args.get('next')
                if next_loc:
                    return redirect(url_for(next_loc))
                else:
                    return redirect(url_for('admin'))
            flash("Credentials are incorrect", "error")
            return render_template("admin/login.html", form=form)
        return render_template("admin/login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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
    modules_query = Module.query
    if not modules_query.all():
        return render_template("modules.html")
    if area_term and area_term != '':
        modules_query = modules_query.filter(Module.units.any(Unit.area.has(Area.name == area_term)))
    if unit_term and unit_term != '':
        modules_query = modules_query.filter(Module.units.any(Unit.name == unit_term))
    if keyword_term and keyword_term != '':
        modules_query = modules_query.filter(Module.keywords.any(Keyword.name == keyword_term))
    if search_term and search_term != '':
        modules_query = Module.query.filter(or_(
            Module.name.ilike(f'%{search_term}%'),
            Module.units.any(or_(
                Unit.name.ilike(f'%{search_term}%'),
                Unit.area.has(Area.name.ilike(f'%{search_term}%'))
            )),
            Module.keywords.any(or_(
                Keyword.name.ilike(f'%{search_term}%'),
                Keyword.acronym.ilike(f'%{search_term}%')
            )),
            Module.author.ilike(f'%{search_term}%')
        ))
    return render_template("modules.html",
                           modules=modules_query.order_by(Module.date_updated.desc(), Module.date_added.desc()).all(),
                           search=search_term)


@app.route('/contribute')
def contribute():
    return render_template("contribute.html")


@app.route('/upload', methods=['POST'])
@login_required
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
    return json.dumps([file[1].id for file in to_save]), 200


@app.route('/download/<file_id>')
def download(file_id):
    file_to_download = File.query.filter(File.id == file_id).first()
    if not file_to_download:
        abort(404)
    return send_from_directory(app.config["UPLOAD_PATH"], str(file_to_download.id), as_attachment=True,
                               download_name=file_to_download.name)


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


@app.route('/admin')
@login_required
def admin():
    return render_template('admin/index.html')


@app.route('/admin/add_module', methods=['GET', 'POST'])
@login_required
def add_module():
    if request.method == 'GET':
        keywords = Keyword.query.all()
        areas = Area.query.all()
        return render_template('admin/add_module.html', keywords=keywords, areas=areas)
    elif request.method == 'POST':
        params = request.get_json()
        files = File.query.filter(File.id.in_(params["file_ids"])).all()
        print(files)
        keywords = Keyword.query.filter(Keyword.id.in_(params["keyword_ids"])).all()
        print(keywords)
        units = Unit.query.filter(Unit.id.in_(params["unit_ids"])).all()
        print(units)
        links = []
        for url in params["links"].split():
            link = Link.query.filter(Link.url == url).first()
            if not link:
                link = Link(url=url)
                db.session.add(link)
            links.append(link)
        db.session.commit()
        print(links)
        new_module = Module(name=params["name"], author=params["author"], description=params["description"],
                            notes=params["notes"], units=units, files=files, keywords=keywords, links=links)
        try:
            db.session.add(new_module)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as err:
            db.session.rollback()
            for file in files:
                db.session.delete(file)
                db.session.commit()
            return {"code": 500, "data": "", "msg": err.orig.args}
        return {"code": 200, "data": "", "msg": "OK"}


@app.route('/admin/edit_module', methods=['GET'])
@login_required
def edit():
    if request.method == 'GET':
        search_term = request.args.get('search')
        area_term = request.args.get('area')
        unit_term = request.args.get('unit')
        keyword_term = request.args.get('keyword')
        modules_query = Module.query
        if not modules_query.all():
            return render_template("modules.html")
        if area_term and area_term != '':
            modules_query = modules_query.filter(Module.units.any(Unit.area.has(Area.name == area_term)))
        if unit_term and unit_term != '':
            modules_query = modules_query.filter(Module.units.any(Unit.name == unit_term))
        if keyword_term and keyword_term != '':
            modules_query = modules_query.filter(Module.keywords.any(Keyword.name == keyword_term))
        if search_term and search_term != '':
            modules_query = Module.query.filter(or_(
                Module.name.ilike(f'%{search_term}%'),
                Module.units.any(or_(
                    Unit.name.ilike(f'%{search_term}%'),
                    Unit.area.has(Area.name.ilike(f'%{search_term}%'))
                )),
                Module.keywords.any(or_(
                    Keyword.name.ilike(f'%{search_term}%'),
                    Keyword.acronym.ilike(f'%{search_term}%')
                )),
                Module.author.ilike(f'%{search_term}%')
            ))
        return render_template("admin/modules.html", modules=modules_query.order_by(Module.date_updated.desc(),
                                                                                    Module.date_added.desc()).all(),
                               search=search_term)


@app.route('/admin/edit_module/<module_id>', methods=['GET', 'POST'])
@login_required
def edit_module(module_id):
    if request.method == 'GET':
        module_to_edit = Module.query.filter(Module.id == module_id).first()
        keywords = Keyword.query.all()
        areas = Area.query.all()
        return render_template('admin/edit_module.html', keywords=keywords, areas=areas, module=module_to_edit)
    elif request.method == 'POST':
        params = request.get_json()
        files = File.query.filter(File.id.in_(params["file_ids"])).all()
        print(files)
        keywords = Keyword.query.filter(Keyword.id.in_(params["keyword_ids"])).all()
        print(keywords)
        units = Unit.query.filter(Unit.id.in_(params["unit_ids"])).all()
        print(units)
        links = []
        for url in params["links"].split():
            link = Link.query.filter(Link.url == url).first()
            if not link:
                link = Link(url=url)
                db.session.add(link)
            links.append(link)
        db.session.commit()
        print(links)
        new_module = Module(name=params["name"], author=params["author"], description=params["description"],
                            notes=params["notes"], units=units, files=files, keywords=keywords, links=links)
        try:
            db.session.add(new_module)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as err:
            db.session.rollback()
            for file in files:
                db.session.delete(file)
                db.session.commit()
            return {"code": 500, "data": "", "msg": err.orig.args}
        return {"code": 200, "data": "", "msg": "OK"}


def load_areas():
    with open(".data/database/area_units_edited.json", "r") as file:
        areas = json.load(file)
    for area in areas:
        units = [Unit(name=unit) for unit in areas[area]]
        new_area = Area(name=area, units=units)
        db.session.add(new_area)
    db.session.commit()


def load_keywords():
    with open(".data/database/keywords_edited.json", "r") as file:
        keywords = json.load(file)
    sources = []
    for keyword in keywords:
        for source in keywords[keyword]["sources"]:
            new_source = Source(name=source)
            if source not in sources:
                sources.append(source)
                db.session.add(new_source)
        sources_list = [Source.query.filter(Source.name == source).first() for source in keywords[keyword]["sources"]]
        new_keyword = Keyword(name=keyword, acronym=keywords[keyword]["acronym"], sources=sources_list)
        db.session.add(new_keyword)
    db.session.commit()


if __name__ == '__main__':
    app.run()
