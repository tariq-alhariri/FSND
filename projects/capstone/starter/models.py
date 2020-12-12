import enum
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy.orm import relationship, backref



DATABASE_NAME = "agency"
username = 'postgres'
password = '123456'
url = 'localhost:5432'
database_path = "postgres://{}:{}@{}/{}".format(username, password, url, DATABASE_NAME)

db = SQLAlchemy()
moment = Moment()
'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    migrate = Migrate(app, db)
    db.init_app(app)
    db.create_all()

'''
Movie

'''


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    PREFER_NOT_TO_SHARE = "prefer not to share"


class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    release_date = db.Column(db.DateTime)
    actors = db.relationship('Actor',secondary='movies_actors')


    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
          'id': self.id,
          'title': self.title,
          'release_date': self.release_date,
        }


'''
Actor

'''
class Actor(db.Model):
    __tablename__ = 'actors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    age = db.Column(db.Integer)
    gender = db.Column(db.Enum(Gender))
    movies = db.relationship('Movie',secondary='movies_actors')



    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender


    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
          'id': self.id,
          'name': self.name,
          'age': self.age,
          'gender': self.gender.value,
        }


class MovieActor(db.Model):
    __tablename__ = 'movies_actors'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('actors.id'))
    actor_id = db.Column(db.Integer, db.ForeignKey('movies.id'))