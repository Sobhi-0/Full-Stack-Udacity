#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
from logging import FileHandler, Formatter

# needed to decide what are the past/upcoming shows
from datetime import datetime

import babel
import dateutil.parser
from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for, jsonify)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_wtf import Form

from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
# done in the config.py file

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    # genres are seperated by comma and a space (to use .split(", ") when a list is needed)
    genres = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    venue = db.relationship("Show", backref=db.backref("venue", cascade="all, delete"))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres are seperated by comma and a space (to use .split(", ") when a list is needed)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref=db.backref("artist", cascade="all, delete"))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "show_table"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    start_time = db.Column(db.DateTime, nullable=False)

    # this method is to return a list of upcoming/past shows
    @staticmethod
    def venue_shows(venue_id, period):
         # shows is a list of query objects so it will need iteration to acces each show individually
        shows = Show.query.filter_by(venue_id=venue_id).all()
        
        # define two lists to add the dictionaries in them based on the whether the event is in the past or future
        past = []
        upcoming = []
        for show in shows:
            # to access fields in the Artist Model
            artist = show.artist
            temp_dict = {}
            temp_dict["artist_id"] = show.artist_id
            temp_dict["artist_name"] = artist.name
            temp_dict["artist_image_link"] = artist.image_link
            # convert it to string because parsal needs it to be string not datetime
            temp_dict["start_time"] = str(show.start_time)

            if show.start_time > datetime.now():
                upcoming.append(temp_dict)
            else:
                past.append(temp_dict)

        # return depends on what is neede
        if period == "upcoming":
            return upcoming
        elif period == "past":
            return past

    @staticmethod
    def artist_shows(artist_id, period):
        # shows is a list of query objects so it will need iteration to acces each show individually
        shows = Show.query.filter_by(artist_id=artist_id).all()
        
        # define two lists to add the dictionaries in them based on the whether the event is in the past or future
        past = []
        upcoming = []
        for show in shows:
            # to access fields in the Venue Model
            venue = show.venue
            if venue:
                temp_dict = {}
                temp_dict["venue_id"] = show.venue_id
                temp_dict["venue_name"] = venue.name
                temp_dict["venue_image_link"] = venue.image_link
                # convert it to string because parsal needs it to be string not datetime
                temp_dict["start_time"] = str(show.start_time)

                if show.start_time > datetime.now():
                    upcoming.append(temp_dict)
                else:
                    past.append(temp_dict)

        # return depends on what is neede
        if period == "upcoming":
            return upcoming
        elif period == "past":
            return past

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

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.order_by(Venue.state).all()

    # prepare the list of dictionaries each dict has three values the third one is a list of dicts
    data = []
    for venue in venues:
        city_dict = {}
        city_dict["city"] = venue.city
        city_dict["state"] = venue.state
        city_dict["venues"] = []
        if city_dict not in data:
            data.append(city_dict)

    # fills the inner list of dictionaries (i refers to the list)
    for i in data:    
        for venue in venues:
            venue_dict = {}
            if i["city"] == venue.city and i["state"] == venue.state:
                venue_dict["id"] = venue.id
                venue_dict["name"] = venue.name
                venue_dict["num_upcoming_shows"] = len(Show.venue_shows(venue.id, "upcoming"))
                i["venues"].append(venue_dict)

    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    # get what the user searched for
    search_term = request.form.get('search_term', '')
    venues = Venue.query.order_by(Venue.name).all()
    
    # change to lowe case to make it "case-insensitive"
    search = search_term.lower()
    data = []

    for venue in venues:
        if search in venue.name.lower():
            temp_dict = {}

            temp_dict["id"] = venue.id
            temp_dict["name"] = venue.name
            temp_dict["num_upcoming_shows"] = len(Show.venue_shows(venue.id, "upcoming"))
        
            data.append(temp_dict)

    response={
    "count": len(data),
    "data": data
    }
    
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    
    # define two lists to add the dictionaries in them based on the whether the event is in the past or future
    # this is done in the method defined in Show model
    past = Show.venue_shows(venue_id, "past")
    upcoming = Show.venue_shows(venue_id, "upcoming")

    data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(", "),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm(request.form)

    # list of all existing names to make sure there will not be any duplicated venues
    names = db.session.query(Venue.name).all()
    names = [venue[0] for venue in names]

    try:
        # to make sure no duplicate venues are added
        if form.name.data.strip() in names:
            flash("Venue already exists")
            raise NameError

        # makes sure it passes all the validations
        if form.validate():
            venue = Venue(
                # .strip() to make sure spaces at the beginning and at the ending of the string are ignored
                name = form.name.data.strip(),
                city = form.city.data.strip(),
                state = form.state.data,
                address = form.state.data.strip(),
                phone = form.phone.data.strip(),
                facebook_link = form.facebook_link.data.strip(),
                image_link = form.image_link.data.strip(),
                website = form.website_link.data.strip(),
                seeking_talent = form.seeking_talent.data,
                seeking_description = form.seeking_description.data.strip(),
                # .join() used to keep up with the assumption in the Model (string seperated by comma and a space to be converted to a list later)
                genres =  ', '.join(request.form.getlist("genres"))
            )
        with app.app_context():
            db.session.add(venue)
            db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        with app.app_context():
            db.session.rollback()
        # prints the error
        print("ERROR:", e)
        # so it shows exactly what the user miss-entered in the create form (if there is any)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in field "{field}": {error}')

        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        with app.app_context():
            db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        with app.app_context():
            venue = Venue.query.get(venue_id)
            temp = venue.name[::]
            db.session.delete(venue)
            db.session.commit()
            flash(f'Venue {temp} was deleted successfully')
    except Exception as e:
        error = True
        print("ERROR:", e)
        with app.app_context():
            db.session.rollback()
            flash(f'Venue {temp} was not deleted')
    finally:
        with app.app_context():
            db.session.close()
    if not error:
        return jsonify({ 'success': True })
    else:
        return jsonify({ 'success': False })

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # DID IT YAYYY!!!
    # check show_venue.html (to see the delete button) the return happens there

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.order_by(Artist.name).all()

    data = []
    for artist in artists:
        temp_dict = {}
        temp_dict["id"] = artist.id
        temp_dict["name"] = artist.name
        data.append(temp_dict)

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    # get what the user searched for
    search_term = request.form.get('search_term', '')
    artists = Artist.query.all()

    # change to lowe case to make it "case-insensitive"
    search = search_term.lower()
    data = []
    for artist in artists:
        if search in artist.name.lower():
            temp_dict = {}

            temp_dict["id"] = artist.id
            temp_dict["name"] = artist.name
            temp_dict["num_upcoming_shows"] = len(Show.artist_shows(artist.id, "upcoming"))
        
            data.append(temp_dict)

    response={
    "count": len(data),
    "data": data
    }
    
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)

    past = Show.artist_shows(artist_id, "past")
    upcoming = Show.artist_shows(artist_id, "upcoming")

    data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(", "),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
        }
    
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm(request.form)
        with app.app_context():
            artist = Artist.query.get(artist_id)

            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.image_link = form.image_link.data
            artist.genres = ", ".join(form.genres.data)
            artist.facebook_link = form.facebook_link.data
            artist.website = form.website_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data

            db.session.commit()
    except Exception as e:
        print("ERROR:", e)
        with app.app_context():
            db.session.rollback()
    finally:
        with app.app_context():
            db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        form = VenueForm(request.form)
        with app.app_context():
            venue = Venue.query.get(venue_id)
            
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.genres = ", ".join(form.genres.data)
            venue.facebook_link = form.facebook_link.data
            venue.website = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            db.session.commit()
    except Exception as e:
        print("ERROR:", e)
        with app.app_context():
            db.session.rollback()
    finally:
        with app.app_context():
            db.session.close()

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

    form = ArtistForm(request.form)

    # list of all existing names to make sure there will not be any duplicated artists
    names = db.session.query(Artist.name).all()
    names = [artist[0] for artist in names]

    try:
        # to make sure no duplicate venues are added
        if form.name.data.strip() in names:
            flash("Artist already exists")
            raise NameError
        # makes sure it passes all the validations
        if form.validate():
            artist = Artist(
                # .strip() to make sure spaces at the beginning and at the ending of the string are ignored
                name = form.name.data.strip(),
                city = form.city.data.strip(),
                state = form.state.data,
                phone = form.phone.data.strip(),
                facebook_link = form.facebook_link.data.strip(),
                image_link = form.image_link.data.strip(),
                website = form.website_link.data.strip(),
                seeking_venue = form.seeking_venue.data,
                seeking_description = form.seeking_description.data.strip(),
                # .join() used to keep up with the assumption in the Model (string seperated by comma and a space to be converted to a list later)
                genres =  ', '.join(request.form.getlist("genres"))
            )
        with app.app_context():
            db.session.add(artist)
            db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        with app.app_context():
            db.session.rollback()
        # prints the error
        print("ERROR:", e)
        # so it shows exactly what the user miss-entered in the create form (if there is any)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in field "{field}": {error}')

        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        with app.app_context():
            db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    
    data = []
    for show in shows:
        temp_dict = {}
        venue = show.venue
        # to make sure that there is no show with a deleted venue
        if venue:
            artist = show.artist

            temp_dict["venue_id"] = show.venue_id
            temp_dict["venue_name"] = venue.name
            temp_dict["artist_id"] = show.artist_id
            temp_dict["artist_name"] = artist.name
            temp_dict["artist_image_link"] = artist.image_link
            temp_dict["start_time"] = str(show.start_time)
            
            data.append(temp_dict)

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

    form = ShowForm(request.form)
    
    try:
        if form.validate():
            show = Show(
                artist_id = form.artist_id.data,
                venue_id = form.venue_id.data,
                start_time = form.start_time.data
            )
        with app.app_context():
            db.session.add(show)
            db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        print("ERROR:", e)
        with app.app_context():
            db.session.rollback()

        # shows exactly what the user miss-entered in the create form (if there is any)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in field "{field}": {error}')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        flash("An error occurred. Show could not be listed.")
    finally:
        with app.app_context():
            db.session.close()

    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
