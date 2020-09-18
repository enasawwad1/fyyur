from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from app import app
from setup import setup_db

db = setup_db(app=app)


# ----------------------------------------------------------------------------
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(500), nullable=True)
    genres = db.Column(ARRAY(String), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='List', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    genres = db.Column(ARRAY(String), nullable=False)
    address = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='List', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    show_title = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    register_link = db.Column(db.String(500), nullable=True)
