from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, ValidationError, \
    SubmitField
from wtforms.validators import DataRequired, AnyOf, URL, Length
import re

state_choices = [('AL', 'AL'),
                 ('AK', 'AK'),
                 ('AZ', 'AZ'),
                 ('AR', 'AR'),
                 ('CA', 'CA'),
                 ('CO', 'CO'),
                 ('CT', 'CT'),
                 ('DE', 'DE'),
                 ('DC', 'DC'),
                 ('FL', 'FL'),
                 ('GA', 'GA'),
                 ('HI', 'HI'),
                 ('ID', 'ID'),
                 ('IL', 'IL'),
                 ('IN', 'IN'),
                 ('IA', 'IA'),
                 ('KS', 'KS'),
                 ('KY', 'KY'),
                 ('LA', 'LA'),
                 ('ME', 'ME'),
                 ('MT', 'MT'),
                 ('NE', 'NE'),
                 ('NV', 'NV'),
                 ('NH', 'NH'),
                 ('NJ', 'NJ'),
                 ('NM', 'NM'),
                 ('NY', 'NY'),
                 ('NC', 'NC'),
                 ('ND', 'ND'),
                 ('OH', 'OH'),
                 ('OK', 'OK'),
                 ('OR', 'OR'),
                 ('MD', 'MD'),
                 ('MA', 'MA'),
                 ('MI', 'MI'),
                 ('MN', 'MN'),
                 ('MS', 'MS'),
                 ('MO', 'MO'),
                 ('PA', 'PA'),
                 ('RI', 'RI'),
                 ('SC', 'SC'),
                 ('SD', 'SD'),
                 ('TN', 'TN'),
                 ('TX', 'TX'),
                 ('UT', 'UT'),
                 ('VT', 'VT'),
                 ('VA', 'VA'),
                 ('WA', 'WA'),
                 ('WV', 'WV'),
                 ('WI', 'WI'),
                 ('WY', 'WY'),
                 ]
genres_choices = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]


class ShowForm(Form):
    title = StringField(
        'title', validators=[DataRequired()]
    )
    artist_id = StringField(
        'artist_id', validators=[DataRequired()],

    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired()],

    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )
    description = StringField(
        'description', validators=[Length(max=500)]
    )
    register_link = StringField(
        'image_link', validators=[URL(), Length(max=500)]
    )


class VenueForm(Form):
    def validate_phone(form, field):
        if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data):
            raise ValidationError("Invalid phone number.")

    def validate_genres(form, field):
        genres_values = [choice[1] for choice in genres_choices]
        for value in field.data:
            if value not in genres_values:
                raise ValidationError('Invalid genres value.')

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(), Length(max=120)],
        choices=state_choices
    )
    address = StringField(
        'address', validators=[Length(max=120)]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Length(max=120)]
    )
    image_link = StringField(
        'image_link', validators=[URL(), Length(max=500)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Length(max=500)]
    )

    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=500)]
    )
    submit = SubmitField('Submit')


class ArtistForm(Form):
    def validate_phone(form, field):
        if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data):
            raise ValidationError("Invalid phone number.")

    def validate_genres(form, field):
        genres_values = [choice[1] for choice in genres_choices]
        for value in field.data:
            if value not in genres_values:
                raise ValidationError('Invalid genres value.')

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(), Length(max=120)],
        choices=state_choices
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Length(max=120)]
    )
    image_link = StringField(
        'image_link', validators=[URL(), Length(max=500)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Length(max=120)]
    )
    address = StringField(
        'address', validators=[Length(max=120)]
    )
    website = StringField(
        'website', validators=[URL(), Length(max=500)]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=500)]
    )
    submit = SubmitField('Submit')

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
