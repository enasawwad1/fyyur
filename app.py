# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_moment import Moment
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import abort

from forms import *
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
from helpers import get_datetime_now, convert_string_to_datetime
from models import Artist, Venue, Show, db_setup

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app=app)


#
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Get all city and state exits on venue rows
    city_state_list = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    data = []
    # Get all venues match with  city and state  on venue rows

    for item in city_state_list:
        venues_list = []
        venue_query_list = Venue.query.filter_by(city=item[0], state=item[1]).all()
        for venue in venue_query_list:
            venues_list.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    [show for show in venue.shows if
                     convert_string_to_datetime(show.start_time) >= get_datetime_now()]) if len(
                    venue.shows) != 0 else 0,
            })
        data.append({
            "city": item[0],
            "state": item[1],
            "venues": venues_list
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    data = []
    venue_search_term = request.form['search_term']
    if ',' in venue_search_term:
        city_search_term = venue_search_term.split(',')[0]
        state_search_term = venue_search_term.split(',')[1]
        venue_list = Venue.query.filter(Venue.city.ilike('%' + city_search_term + '%'),
                                        Venue.state.ilike('%' + state_search_term + '%')).all()
    else:
        venue_list = Venue.query.filter(Venue.name.ilike('%' + venue_search_term + '%')).all()
    for venue in venue_list:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(
                [show for show in venue.shows if
                 convert_string_to_datetime(show.start_time) >= get_datetime_now()]) if len(
                venue.shows) != 0 else 0,
        })
    response = {
        "count": len(venue_list),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue_details = Venue.query.get(venue_id)
    upcoming_shows_list = []
    past_shows_list = []

    upcoming_shows = [show for show in venue_details.shows if
                      convert_string_to_datetime(show.start_time) > get_datetime_now()] if len(
        venue_details.shows) != 0 else []
    past_shows = [show for show in venue_details.shows if
                  convert_string_to_datetime(show.start_time) < get_datetime_now()] if len(
        venue_details.shows) != 0 else []
    for show in upcoming_shows:
        upcoming_shows_list.append({
            "artist_id": show.artist_id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time,
            "title": show.show_title,
            "register_link": show.register_link,
            "description": show.description

        })
    for show in past_shows:
        past_shows_list.append({
            "artist_id": show.artist_id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time,
            "title": show.show_title,
            "register_link": show.register_link,
            "description": show.description
        })

    data = {
        "id": venue_details.id,
        "name": venue_details.name,
        "genres": venue_details.genres,
        "address": venue_details.address,
        "city": venue_details.city,
        "state": venue_details.state,
        "phone": venue_details.phone,
        "facebook_link": venue_details.facebook_link,
        "seeking_talent": venue_details.seeking_talent,
        "seeking_description": venue_details.seeking_description,
        "image_link": venue_details.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    name = request.form['name']
    seeking_talent_value = None
    try:
        form = VenueForm(request.form)
        if form.validate_on_submit():
            if 'seeking_talent' in request.form:
                if request.form['seeking_talent'] == 'y':
                    seeking_talent_value = True
            city = request.form['city']
            state = request.form['state']
            phone = request.form['phone']
            address = request.form['address']
            genres = request.form.getlist('genres')
            facebook_link = request.form['facebook_link']
            image_link = request.form['image_link']
            seeking_talent = seeking_talent_value if seeking_talent_value is not None else False
            seeking_description = request.form['seeking_description']
            venue = Venue(name=name, city=city, state=state, phone=phone, address=address,
                          genres=genres, facebook_link=facebook_link, image_link=image_link,
                          seeking_talent=seeking_talent, seeking_description=seeking_description)
            db.session.add(venue)
            db.session.commit()

    except SQLAlchemyError as e:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + name + ' could not be listed.')
        else:
            flash('Venue ' + name + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists_list = Artist.query.all()
    data = []
    for artist in artists_list:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    data = []
    artist_search_term = request.form['search_term']

    if ',' in artist_search_term:
        city_search_term = artist_search_term.split(',')[0]
        state_search_term = artist_search_term.split(',')[1]
        artist_list = Artist.query.filter(Artist.city.ilike('%' + city_search_term + '%'),
                                          Artist.state.ilike('%' + state_search_term + '%')).all()
    else:
        artist_list = Artist.query.filter(Artist.name.ilike('%' + artist_search_term + '%')).all()
    for artist in artist_list:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(
                [show for show in artist.shows if
                 convert_string_to_datetime(show.start_time) >= get_datetime_now()]) if len(
                artist.shows) != 0 else 0
        })
    response = {
        "count": len(artist_list),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist_details = Artist.query.get(artist_id)
    upcoming_shows_list = []
    past_shows_list = []

    upcoming_shows = [show for show in artist_details.shows if
                      convert_string_to_datetime(show.start_time) > get_datetime_now()] if len(
        artist_details.shows) != 0 else []
    past_shows = [show for show in artist_details.shows if
                  convert_string_to_datetime(show.start_time) < get_datetime_now()] if len(
        artist_details.shows) != 0 else []
    for show in upcoming_shows:
        upcoming_shows_list.append({
            "venue_id": show.venue_id,
            "venue_name": show.Venue.name,
            "venue_image_link": show.Venue.image_link,
            "start_time": show.start_time,
            "title": show.show_title,
            "register_link": show.register_link,
            "description": show.description

        })
    for show in past_shows:
        past_shows_list.append({
            "venue_id": show.venue_id,
            "venue_name": show.Venue.name,
            "venue_image_link": show.Venue.image_link,
            "start_time": show.start_time,
            "title": show.show_title,
            "register_link": show.register_link,
            "description": show.description
        })

    data = {
        "id": artist_details.id,
        "name": artist_details.name,
        "genres": artist_details.genres,
        "address": artist_details.address,
        "city": artist_details.city,
        "state": artist_details.state,
        "phone": artist_details.phone,
        'website': artist_details.website,
        "facebook_link": artist_details.facebook_link,
        "seeking_talent": artist_details.seeking_talent,
        "seeking_description": artist_details.seeking_description,
        "image_link": artist_details.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_details = Artist.query.get(artist_id)
    artist = {
        "id": artist_details.id,
        "name": artist_details.name,
        "genres": ''.join(map(str, artist_details.genres)),
        "address": artist_details.address,
        "city": artist_details.city,
        "state": artist_details.state,
        "phone": artist_details.phone,
        'website': artist_details.website,
        "facebook_link": artist_details.facebook_link,
        "seeking_talent": artist_details.seeking_talent,
        "seeking_description": artist_details.seeking_description,
        "image_link": artist_details.image_link,
    }
    form.name.data = artist_details.name
    form.genres.data = ''.join(map(str, artist_details.genres))
    form.address.data = artist_details.address
    form.city.data = artist_details.city
    form.state.data = artist_details.state
    form.phone.data = artist_details.phone
    form.website.data = artist_details.website.replace('}', '').replace('{', '')
    form.facebook_link.data = artist_details.facebook_link
    form.seeking_talent.data = artist_details.seeking_talent
    form.seeking_description.data = artist_details.seeking_description
    form.image_link.data = artist_details.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    seeking_talent_value = False
    try:
        form = ArtistForm(request.form)
        if form.validate_on_submit():
            if 'seeking_talent' in request.form:
                if request.form['seeking_talent'] == 'y':
                    seeking_talent_value = True
            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = request.form['phone']
            artist.address = request.form['address']
            artist.website = request.form['website']
            artist.genres = request.form.getlist('genres')
            artist.facebook_link = request.form['facebook_link']
            artist.image_link = request.form['image_link']
            artist.seeking_talent = seeking_talent_value if seeking_talent_value is not None else False
            artist.seeking_description = request.form['seeking_description']
            db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_details = Venue.query.get(venue_id)
    venue = {
        "id": venue_details.id,
        "name": venue_details.name,
        "genres": venue_details.genres,
        "address": venue_details.address,
        "city": venue_details.city,
        "state": venue_details.state,
        "phone": venue_details.phone,
        "facebook_link": venue_details.facebook_link,
        "seeking_talent": venue_details.seeking_talent,
        "seeking_description": venue_details.seeking_description,
        "image_link": venue_details.image_link,
    }
    form.name.data = venue_details.name
    form.genres.data = venue_details.genres
    form.address.data = venue_details.address
    form.city.data = venue_details.city
    form.state.data = venue_details.state
    form.phone.data = venue_details.phone
    form.facebook_link.data = venue_details.facebook_link
    form.seeking_talent.data = venue_details.seeking_talent
    form.seeking_description.data = venue_details.seeking_description
    form.image_link.data = venue_details.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    seeking_talent_value = None
    try:
        form = VenueForm(request.form)
        if form.validate_on_submit():
            if 'seeking_talent' in request.form:
                if request.form['seeking_talent'] == 'y':
                    seeking_talent_value = True
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.phone = request.form['phone']
            venue.address = request.form['address']
            venue.genres = request.form.getlist('genres')
            venue.facebook_link = request.form['facebook_link']
            venue.image_link = request.form['image_link']
            venue.seeking_talent = seeking_talent_value if seeking_talent_value is not None else False
            venue.seeking_description = request.form['seeking_description']
            db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/shows/<int:show_id>/edit', methods=['GET'])
def edit_show(show_id):
    form = ShowForm()
    show_details = Show.query.get(show_id)
    show = {
        "id": show_details.id,
        "title": show_details.show_title,
        "artist_id": show_details.artist_id,
        "venue_id": show_details.venue_id,
        "register_link": show_details.register_link,
        "description": show_details.description,
        "start_time": convert_string_to_datetime(show_details.start_time),
    }
    form.title.data = show_details.show_title
    form.artist_id.data = show_details.artist_id
    form.venue_id.data = show_details.venue_id
    form.register_link.data = show_details.register_link
    form.description.data = show_details.description
    form.start_time.data = convert_string_to_datetime(show_details.start_time)
    return render_template('forms/edit_show.html', form=form, show=show)


@app.route('/shows/<int:show_id>/edit', methods=['POST'])
def edit_show_submission(show_id):
    show = Show.query.get(show_id)
    try:
        form = ShowForm(request.form)
        if form.validate_on_submit():
            show.show_title = request.form['title']
            show.artist_id = request.form['artist_id']
            show.venue_id = request.form['venue_id']
            show.register_link = request.form['register_link']
            show.start_time = request.form['start_time']
            show.description = request.form['description']
            db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('shows'))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    name = request.form['name']
    seeking_talent_value = None
    try:
        form = ArtistForm(request.form)
        if form.validate_on_submit():
            if 'seeking_talent' in request.form:
                if request.form['seeking_talent'] == 'y':
                    seeking_talent_value = True
            city = request.form['city']
            state = request.form['state']
            phone = request.form['phone']
            address = request.form['address']
            genres = request.form.getlist('genres')
            website = request.form.getlist('website')
            facebook_link = request.form['facebook_link']
            image_link = request.form['image_link']
            seeking_talent = seeking_talent_value if seeking_talent_value is not None else False
            seeking_description = request.form['seeking_description']
            artist = Artist(name=name, city=city, state=state, phone=phone, address=address, website=website,
                            genres=genres, facebook_link=facebook_link, image_link=image_link,
                            seeking_talent=seeking_talent, seeking_description=seeking_description)
            db.session.add(artist)
            db.session.commit()
        else:
            error = True
    except SQLAlchemyError as e:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' + name + ' could not be listed.')
        else:
            flash('Artist ' + name + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
    error = False
    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify({'success': True})


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows_list = Show.query.all()
    data = []
    for show in shows_list:
        data.append({
            "id": show.id,
            "title": show.show_title,
            "venue_id": show.venue_id,
            "venue_name": show.Venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time,
            "description": show.description,
            "register_link": show.register_link
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    show_title = request.form['title']
    try:
        form = ShowForm(request.form)
        if form.validate_on_submit():
            artist_id = request.form['artist_id']
            venue_id = request.form['venue_id']
            start_time = request.form['start_time']
            description = request.form['description']
            register_link = request.form.getlist('register_link')
            show = Show(show_title=show_title, artist_id=artist_id, venue_id=venue_id, description=description,
                        start_time=start_time, register_link=register_link)
            db.session.add(show)
            db.session.commit()

    except SQLAlchemyError as e:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show with title ' + show_title + ' could not be listed.')
        else:
            flash('Show ' + show_title + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/shows/<show_id>/delete', methods=['DELETE'])
def delete_show(show_id):
    error = False
    try:
        Show.query.filter_by(id=show_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify({'success': True})


@app.route('/shows/search', methods=['POST'])
def search_shows():
    data = []
    show_search_term = request.form['search_term']
    shows_list = Show.query.filter(Show.show_title.ilike('%' + show_search_term + '%')).all()
    for show in shows_list:
        data.append({
            "id": show.id,
            "title": show.show_title,
            "venue_id": show.venue_id,
            "venue_name": show.Venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time,
            "description": show.description,
            "register_link": show.register_link
        })
    response = {
        "count": len(shows_list),
        "data": data
    }
    return render_template('pages/search_shows.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
