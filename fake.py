from faker import Faker
from app import db, Area, Unit, Module, Keyword, File, Link, Source
import json
from datetime import date, datetime

fake = Faker()
Faker.seed(0)


def fill_with_fake(fake_auk=True):
    if fake_auk:
        random_areas(14)
        random_keywords(400)
    else:
        load_keywords()
        load_areas()
    random_files(100)
    random_urls(120)
    random_modules(100)


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


def random_modules(n):
    areas = Area.query.all()
    keywords = Keyword.query.all()
    files = File.query.all()
    links = Link.query.all()
    for i in range(n):
        new_module = Module(name=fake.catch_phrase(), author=fake.name(), description=fake.paragraph(nb_sentences=4), date_added=fake.date_between_dates(date.fromisoformat('2018-01-01'), date.today()))
        db.session.add(new_module)
        db.session.commit()
    modules = Module.query.all()
    for module in modules:
        chosen_area = fake.random_element(areas)
        chosen_units = list(set([fake.random_element(chosen_area.units) for j in range(fake.random_int(min=1, max=2))]))
        chosen_keywords = list(set([fake.random_element(keywords) for j in range(fake.random_int(min=2, max=4))]))
        chosen_files = list(set([fake.random_element(files) for j in range(fake.random_int(min=1, max=3))]))
        chosen_links = list(set([fake.random_element(links) for j in range(fake.random_int(min=2, max=5))]))
        module.units = chosen_units
        module.keywords = chosen_keywords
        module.files = chosen_files
        module.links = chosen_links
        db.session.commit()


def random_areas(n):
    for i in range(n):
        units = [unit.name for unit in Unit.query.all()]
        new_area = Area(name=fake.word(), units=[Unit(name=word) for word in fake.words(nb=fake.random_int(min=3, max=4)) if word not in units])
        db.session.add(new_area)
    db.session.commit()


def random_files(n):
    for i in range(n):
        files = [file.name for file in File.query.all()]
        name = fake.file_name()
        if name not in files:
            new_file = File(name=name)
            db.session.add(new_file)
    db.session.commit()


def random_keywords(n):
    for i in range(n):
        keywords = [keyword.name for keyword in Keyword.query.all()]
        name = fake.word()
        if name not in keywords:
            new_keyword = Keyword(name=name, acronym=''.join(fake.random_letters(length=3)).upper() if fake.random_int(min=0, max=1) else '')
            db.session.add(new_keyword)
    db.session.commit()


def random_urls(n):
    for i in range(n):
        links = [link.url for link in Link.query.all()]
        url = fake.domain_name()
        if url not in links:
            new_url = Link(url=url)
            db.session.add(new_url)
    db.session.commit()


def clear_database():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    clear_database()
    fill_with_fake(fake_auk=False)
