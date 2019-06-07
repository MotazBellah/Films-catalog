import os
# import sys
# from sqlalchemy import Column, ForeignKey, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from database_setup import Catalog, Base, Item, User
#
# Base = declarative_base()

# engine = "postgres://gozghnoolwqlce:e240c044a8d290246de3687596659b2770422e7dbab9c478032464be84d91e1e@ec2-54-225-72-238.compute-1.amazonaws.com:5432/d126d0jgnpgkog"
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind=engine)
# session = DBSession()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import *

app = Flask(__name__)
app.secret_key="sdfdsuperfdlkngflkjnlkbgirlsdessexyasspussyfuchyah!!!!!dfghhm;glhjkhjl,.jk"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# Configure database
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


genres = ['Action', 'Comedy', 'Crime', 'Drama', 'Historical', 'Romance', 'Sci-Fi']

for genre in genres:
    type = Catalog(name=genre)
    db.session.add(type)
    db.session.commit()

# item1 = Item(name="Logan", user_id=1,catalog_id=1)
# db.session.add(item1)
# db.session.commit()
#
# item2 = Item(name="The Hangover", user_id=1,catalog_id=2)
# db.session.add(item2)
# db.session.commit()
#
# item3 = Item(name="Pulp Fiction", user_id=1,catalog_id=3)
# db.session.add(item3)
# db.session.commit()
#
# item4 = Item(name="Shawshank Redemption", user_id=1,catalog_id=4)
# db.session.add(item4)
# db.session.commit()
#
# item5 = Item(name="Dunkirk", user_id=1,catalog_id=5)
# db.session.add(item5)
# db.session.commit()
#
# item6 = Item(name="About Time", user_id=1,catalog_id=6)
# db.session.add(item6)
# db.session.commit()
#
# item7 = Item(name="The Martian", user_id=1,catalog_id=7)
# db.session.add(item7)
# db.session.commit()
