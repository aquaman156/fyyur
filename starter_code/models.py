# models.py
from flask_sqlalchemy import SQLAlchemy
import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy(app)
moment = Moment(app)
migrate = Migrate(app, db)
app.config.from_object('config')

class Venue(db.Model):
    __tablename__ = 'Venue'
    # setting attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    # returns my data to html
    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state}>',
        f' <{self.address} {self.phone} {self.image_link} {self.facebook_link}>'

    # -added tables via flask db init | migrate | upgrade

class Artist(db.Model):
    __tablename__ = 'Artist'
    #setting attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    #returns my data to html
    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state}>',
        f' <{self.address} {self.phone} {self.image_link} {self.facebook_link}>'

    # -added tables via flask db init | migrate | upgrade

class Show(db.Model):
    __tablename__ = 'Show'
    # setting attributes
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    shows = db.relationship('Show', backref=db.backref('venues'), lazy="joined")

    def __repr__(self):
        return '<Show {}{}>'.format(self.artist_id, self.venue_id)
