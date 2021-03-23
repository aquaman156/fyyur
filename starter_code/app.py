#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
import models

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = models.app
db = models.db

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # queries Venue and displays created venues
  data = models.Venue.query.all()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # gets search from form
    search = request.form.get('search_term', '')
    # filter search for like terms
    venues = models.Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
    # create response dictionary
    response = {
    'count': len(venues),
    'data': []
    }
    # adds responses to the dictionary per field
    for venue in venues:
        response["data"].append({
        'id': venue.id,
        'name': venue.name
        })

  # done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = models.Venue.query.get(venue_id)
    shows = db.relationship(
    'Show',
    backref=db.backref('venues'),
    lazy="joined"
)
    upcoming_shows = db.session.query(models.Artist, shows).join(shows).join(models.Venue).\
    filter(
        shows.venue_id == venue_id,
        shows.artist_id == models.Artist.id,
        shows.start_time > datetime.now()
    ).\
    all()
    past_shows = []
    for show in venue.shows:
        if show.start_time <= datetime.now():
            past_shows.append({
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'venue_name':show.venue_name,
                'venue_id':show.venue_id,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        })
    all()
    # shows the venue page with the given venue_id
    data ={'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'address':venue.address,
    'phone': venue.phone,
    'genres':venue.genres,
    'facebook_link':venue.facebook_link,
    'image_link': venue.image_link,
    'seeking_talent':venue.seeking_talent,
    'upcoming_shows':upcoming_shows,
    'past_shows':past_shows,
    'start_time':shows.start_time.strftime("%m/%d/%Y, %H:%M")}
    # done: replace with real venue data from the venues table, using venue_id
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
    # getting form data object
    form = VenueForm(request.form)
    try:
        # instantiate Venue Model and set equal to the form data
        venue = models.Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data

        )
    # add and create
        db.session.add(venue)
        db.session.commit()
    # catch error - flash an error and rollback changes
    except ValueError as e:
        print(e)
        error =True
        if error:
            flash('venue could not be listed')
        db.session.rollback()
    # close session and post flash
    finally:
        db.session.close()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        models.Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except ValueError as e:
        print(e)
        flash('venue could not be deleted')
        db.session.rollback()
    finally:
        db.session.close()

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # query the Artist datatable and return its data
  data=models.Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search artists based on form data search
    search = request.form.get('search_term', '')
    artists = models.Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
    # setting up responses
    response = {
    'count': len(artists),
    'data': []
    }
    # add to responses per entry from the Artist query
    for artist in artists:
        response["data"].append({
        'id': artist.id,
        'name': artist.name
        })
    # return data
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # queries Artists and displays the artist's information per their id
    data = models.Artist.query.get(artist_id)
    # returns the data to the front end
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = models.Artist.query.get(artist_id)
    form.name.data=artist.name,
    form.city.data=artist.city,
    form.state.data=artist.state,
    form.phone.data=artist.phone,
    form.genres.data=artist.genres,
    form.facebook_link.data=artist.facebook_link,
    form.image_link.data=artist.image_link

  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    try:
        # instantiate the Artist Model and set values equal to form data
        artist = models.Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
        )
    # add and commit changes
        db.session.add(artist)
        db.session.commit()
    # error catch
    except ValueError as e:
        print(e)
        flash('artist could not be listed')
        db.session.rollback()
    # close session
    finally:
        db.session.close()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # create data list
    data = []
    # query shows and order them by the start times
    shows = models.Show.query.order_by(models.Show.start_time.desc()).all()
    # loop over shows
    for show in shows:
        # query Venue and filter by the show id or 404 error out
        venue = models.Venue.query.filter_by(id=show.venue_id).first_or_404()
        # query Artist and filter by the show id or 404 error out
        artist = models.Artist.query.filter_by(id=show.artist_id).first_or_404()
        # add to the end of the list, but we are making a list of dictionaries
        data.extend([{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            # this formats the time so it can be parsed properly
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
    # displays list of shows at /shows
    # done: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # done: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    form = ShowForm(request.form)
    try:
        # instantiate Show
        show = models.Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time =form.start_time.data
        )
        # add and submit
        db.session.add(show)
        db.session.commit()

    # if error:
    except:
        flash('show could not be listed')
        db.session.rollback()
    #close session
    finally:
        db.session.close()

    # done: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Show at  ' + request.form['start_time'] + ' was successfully listed!')
    return render_template('pages/home.html')

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
