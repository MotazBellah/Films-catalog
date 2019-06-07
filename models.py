from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """ User model """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    hashed_pswd = db.Column(db.String(), nullable=False)


class Catalog(db.Model):
    __tablename__ = "catalog"

    name = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            }


class Item(db.Model):
    __tablename__ = "item"

    name = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250))
    type = db.Column(db.String(250))
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
    catalog = db.relationship(Catalog)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(User)

    # To use JSON
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
        }
