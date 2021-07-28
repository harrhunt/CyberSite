from faker import Faker
from app import db, Area, Unit, Module, Keyword, File, Link

fake = Faker()
Faker.seed(0)


def fill_with_fake():
    random_areas(7)
    random_keywords(400)
    random_files(25)
    random_urls(40)
    random_modules(10)


def random_modules(n):
    units = Unit.query.all()
    keywords = Keyword.query.all()
    files = File.query.all()
    links = Link.query.all()
    for i in range(n):
        chosen_units = list(set([fake.random_element(units) for j in range(fake.random_int(min=1, max=2))]))
        chosen_keywords = list(set([fake.random_element(keywords) for j in range(fake.random_int(min=2, max=6))]))
        chosen_files = list(set([fake.random_element(files) for j in range(fake.random_int(min=1, max=3))]))
        chosen_links = list(set([fake.random_element(links) for j in range(fake.random_int(min=2, max=5))]))
        new_module = Module(name=fake.catch_phrase(), author=fake.name(), description=fake.paragraph(nb_sentences=4), units=chosen_units, keywords=chosen_keywords, files=chosen_files, links=chosen_links)
        db.session.add(new_module)
    db.session.commit()


def random_areas(n):
    for i in range(n):
        units = [unit.name for unit in Unit.query.all()]
        new_area = Area(name=fake.word(), units=[Unit(name=word) for word in fake.words(nb=fake.random_int(min=3, max=4)) if word not in units])
        db.session.add(new_area)
    db.session.commit()


def random_files(n):
    for i in range(n):
        new_file = File(name=fake.file_name())
        db.session.add(new_file)
    db.session.commit()


def random_keywords(n):
    for i in range(n):
        keywords = [keyword.name for keyword in Keyword.query.all()]
        name = fake.word()
        if name not in keywords:
            new_keyword = Keyword(name=name, acronym=''.join(fake.random_letters(length=3)).upper())
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
    db.session.query(Area).delete()
    db.session.query(Unit).delete()
    db.session.query(Module).delete()
    db.session.query(Keyword).delete()
    db.session.query(File).delete()
    db.session.query(Link).delete()


if __name__ == '__main__':
    clear_database()
    fill_with_fake()
