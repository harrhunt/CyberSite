from flask_sqlalchemy import Model
from sqlalchemy.types import Integer, String, Date
from sqlalchemy import Column
from datetime import date, datetime


class Area(Model):
    __tablename__ = 'areas'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100))


class Unit(Model):
    __tablename__ = 'units'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100))


class Keyword(Model):
    id = Column(Integer(), primary_key=True)
    name = Column(String(100))


class Module(Model):
    __tablename__ = 'keywords'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100))
    author = Column(String(100))
    date_added = Column(Date, default=date.today())
    description = Column(String(8192))
    notes = Column(String(8192))


class File(Model):
    id = Column(Integer(), primary_key=True)
    name = Column(String(200), unique=True)
    date_added = Column(Date, default=date.today())


class Link(Model):
    id = Column(Integer(), primary_key=True)
    url = Column(String(300), unique=True)