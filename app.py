#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for, abort
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *
from config import app
import os 
import collections



collections.Callable = collections.abc.Callable


app.config.from_object('config')

SQLALCHEMY_DATABASE_URI = 'postgresql://david:2834Obegi@localhost:5432/fyyurapp'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []

  venues_at = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  present = datetime.now()
    
  for venue_at in venues_at:
    city = venue_at[0]
    state = venue_at[1]

    location = {'city': city, 'state': state, 'venues': []}

    venues = Venue.query.filter_by(city = city, state=state).all()
    for venue in venues:
      venue_name = venue.name
      venue_id = venue.id
      upcoming_shows = (Show.query.filter_by(venue_id=venue_id)).filter(Show.start_time > present).all()

      location["venues"].append({
        "id": venue_id,
        "name": venue_name,
        "num_upcoming_shows": len(upcoming_shows)
      })
    data.append(location)
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term=request.form.get('search_term', '')
    locations = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    response={
      "count": len(locations),
      "data": locations
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  prev_shows = list(filter(lambda i: i.start_time <
                             datetime.now(), venue.shows))
  next_shows = list(filter(lambda i: i.start_time >=
                                 datetime.now(), venue.shows))

  prev_shows = list(map(lambda i: i.show_artist(), prev_shows))
  next_shows = list(map(lambda i: i.show_artist(), next_shows))

  data = venue.to_dict()
  data['past_shows'] = prev_shows
  data['upcoming_shows'] = next_shows
  data['past_shows_count'] = len(prev_shows)
  data['upcoming_shows_count'] = len(next_shows)

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html') 
  bad_rqst = False
  try:
      venue = Venue()
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.address = request.form.get('address')
      venue.phone = request.form.get('phone')
      og_genres = request.form.getlist('genres')
      venue.genres = ','.join(og_genres)
      venue.facebook_link = request.form.get('facebook_link')
      venue.seeking_talent = True if 'seeking_talent' in request.form else False
      venue.seeking_description = request.form.get('seeking_description')
      venue.website = request.form.get('website')
      db.session.add(venue)
      db.session.commit()
  except:
      bad_rqst = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if bad_rqst:
          flash('An error occured. Venue ' + request.form.get('name') + ' Could not be listed!')
      else:
          flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  v = Venue.query.get(venue_id)
  v_name = v.name
  try:
      v4_deletion = db.session.query.get(venue_id)
      v4_deletion.delete()
      db.session.commit()
      flash("Venue: " + v_name + " was successfully deleted.")

  except:
      db.session.rollback()
      print(sys.exc_info())

  finally:
      db.session.close()
      return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists', methods=['GET'])
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist.id, Artist.name)

  return render_template("pages/artists.html", artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  performers = Artist.query.with_entities(Artist.name, Artist.id).filter(Artist.name.ilike(f"%{search_term}%")).all()
  response={
    "count": len(performers),
    "data": performers
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  prev_shows = list(filter(lambda i: i.start_time <
                           datetime.today(), artist.shows))  
  next_shows = list(filter(lambda i: i.start_time >=
                                 datetime.today(), artist.shows))

  prev_shows = list(map(lambda i: i.show_venue(), prev_shows))
  next_shows = list(map(lambda i: i.show_venue(), next_shows))  

  data = artist.to_dict()
  data['past_shows'] = prev_shows
  data['upcoming_shows'] = next_shows
  data['past_shows_count'] = len(prev_shows)
  data['upcoming_shows_count'] = len(next_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  bad_rqst = False
  try:
      artist = Artist.query.get(artist_id)
      artist.name = request.form.get('name')
      artist.city = request.form.get('city')
      artist.state = request.form.get('state')
      artist.phone = request.form.get('phone')
      og_genres = request.form.getlist('genres')
      artist.genres = ','.join(og_genres)
      artist.website = request.form.get('website')
      artist.image_link = request.form.get('image_link')
      artist.facebook_link = request.form.get('facebook_link')
      artist.seeking_description = request.form.get('seeking_description')
      artist.seeking_venue = True if 'seeking_venue' in request.form else False
      db.session.add(artist)
      db.session.commit()
  except:
      bad_rqst = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if bad_rqst:
          return redirect(url_for('server_error'))
      else:
          return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  bad_rqst = False
  try:
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.address = request.form.get('address')
      venue.phone = request.form.get('phone')
      og_genres = request.form.getlist('genres')
      venue.genres = ','.join(og_genres)
      venue.facebook_link = request.form.get('facebook_link')
      venue.website = request.form.get('website')
      venue.seeking_talent = True if 'seeking_talent' in request.form else False
      venue.seeking_description = request.form.get('seeking_description')
      venue.image_link = request.form.get('image_link')
      db.session.add(venue)
      db.session.commit()
  except:
      bad_rqst = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if bad_rqst:
          flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
      else:
          flash('Venue ' + request.form.get('name') + ' was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  bad_rqst = False
  try:
      artist = Artist()
      artist.name = request.form.get('name')
      artist.city = request.form.get('city')
      artist.state = request.form.get('state')
      artist.phone = request.form.get('phone')
      og_genres = request.form.getlist('genres')
      artist.genres = ','.join(og_genres)
      artist.website = request.form.get('website')
      artist.image_link = request.form.get('image_link')
      artist.facebook_link = request.form.get('facebook_link')
      artist.seeking_description = request.form.get('seeking_description')
      artist.seeking_venue = True if "seeking_venue" in request.form else False
      db.session.add(artist)
      db.session.commit()
  except:
      bad_rqst = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if bad_rqst:
          flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
      else:
          flash('Artist ' + request.form.get('name') + ' was successfully listed!')
      return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  bad_rqst = False
  try:
    show = Show()
    show.artist_id = request.form.get('artist_id'),
    show.venue_id = request.form.get('venue_id'),
    show.start_time = request.form.get('start_time')
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    bad_rqst = True
    print(sys.exc_info())
  finally:
    db.session.close()

    if bad_rqst:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
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
"""if __name__ == '__main__':
    app.run()"""

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
