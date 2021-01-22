from starter_code.app import app, db
from starter_code.models import Venue, Show, Artist
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_wtf import Form
from starter_code.forms import ShowForm, VenueForm, ArtistForm
import babel

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(dt, format='medium'):
  #date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(dt, format)

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

  # Get list of distinct cities/states to group venues by
  distinct_city_state = db.session.query(
    Venue.city, Venue.state, db.func.count(Venue.id)).\
      group_by(Venue.city, Venue.state).all()
  
  new_data = [] 
  for city_state in distinct_city_state:
    city_venues = {
      'city': city_state.city,
      'state': city_state.state,
      'venues': []
    }

    # Get venues for each of the unique city/state combination
    venues = Venue.query.filter(Venue.city == city_state.city).\
      filter(Venue.state == city_state.state).all()
    for venue in venues:
      city_venues['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': venue.num_upcoming_shows
      })
    new_data.append(city_venues)
  
  return render_template('pages/venues.html', areas=new_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

  # Lookup venues by name and return any matching records
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  new_response = {
    'count': len(venues),
    'data': [
      {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': venue.num_upcoming_shows}
      for venue in venues
    ]
  }

  return render_template('pages/search_venues.html', results=new_response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)
  new_data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres.split(','),
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'image_link': venue.image_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description
  }

  # past_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.startTime < datetime.now()).all()
  past_shows = db.session.query(Show).join(Venue).filter(Venue.id == venue_id).filter(Show.startTime < datetime.now()).all()
  new_data['past_shows'] = [{
    'artist_id': show.artist.id,
    'artist_name': show.artist.name,
    'artist_image_link': show.artist.image_link,
    'start_time': show.startTime
  } for show in past_shows]
  new_data['past_shows_count'] = len(past_shows)

  # upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.startTime > datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Venue.id == venue_id).filter(Show.startTime > datetime.now()).all()
  new_data['upcoming_shows'] = [{
    'artist_id': show.artist.id,
    'artist_name': show.artist.name,
    'artist_image_link': show.artist.image_link,
    'start_time': show.startTime
  } for show in upcoming_shows]
  new_data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=new_data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  venue = Venue(
    name = request.form.get('name'),
    genres = ','.join(request.form.getlist('genres')),
    address = request.form.get('address'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    website = request.form.get('website'),
    facebook_link = request.form.get('facebook_link'),
    seeking_talent = request.form.get('seeking_talent') == 'y',
    seeking_description = request.form.get('seeking_description'),
    image_link = request.form.get('image_link')
  )

  try:
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash(f'Failed to list venue {request.form["venue"]}!')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter(Venue.id==venue_id).delete()
    db.session.commit()
    flash(f'Venue {venue_id} deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Failed to delete venue {venue_id}')
  finally:
    db.session.close()

  return 'OK'


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.default = venue.name
  form.genres.default = venue.genres.split(',')
  form.address.default = venue.address
  form.city.default = venue.city
  form.state.default = venue.state
  form.phone.default = venue.phone
  form.website.default = venue.website
  form.facebook_link.default = venue.facebook_link
  form.image_link.default = venue.image_link
  form.seeking_talent.default = venue.seeking_talent
  form.seeking_description.default = venue.seeking_description
  form.process()
  return render_template('forms/edit_venue.html', form=form, venue_id=venue_id, venue_name=venue.name)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.get(venue_id)
  venue.name = request.form.get('name')
  venue.genres = ','.join(request.form.getlist('genres'))
  venue.address = request.form.get('address')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.phone = request.form.get('phone')
  venue.website = request.form.get('website')
  venue.facebook_link = request.form.get('facebook_link')
  venue.seeking_talent = request.form.get('seeking_talent') == 'y'
  venue.seeking_description = request.form.get('seeking_description')
  venue.image_link = request.form.get('image_link')

  try:
    db.session.commit()
    flash(f'Venue {venue_id} updated succesfully')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Failed to updated venue {venue_id}')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = Artist.query.all()
  new_data = [
    {'id': artist.id, 'name': artist.name}
    for artist in artists
  ]
  return render_template('pages/artists.html', artists=new_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  new_response = {
    'count': len(artists),
    'data': [
      {'id': artist.id, 'name': artist.name, 'num_upcoming_shows': artist.num_upcoming_shows}
      for artist in artists
    ]
  }
  return render_template('pages/search_artists.html', results=new_response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  new_data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres.split(','),
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'image_link': artist.image_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description
  }

  # past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.startTime < datetime.now()).all()
  past_shows = db.session.query(Show).join(Artist).filter(Artist.id == artist_id).filter(Show.startTime < datetime.now()).all()
  new_data['past_shows'] = [{
    'venue_id': show.venue_id,
    'venue_name': show.venue.name,
    'venue_image_link': show.venue.image_link,
    'start_time': show.startTime
  } for show in past_shows]
  new_data['past_shows_count'] = len(past_shows)

  # upcoming_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.startTime > datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Artist).filter(Artist.id == artist_id).filter(Show.startTime > datetime.now()).all()
  new_data['upcoming_shows'] = [{
    'venue_id': show.venue.id,
    'venue_name': show.venue.name,
    'venue_image_link': show.venue.image_link,
    'start_time': show.startTime
  } for show in upcoming_shows]
  new_data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=new_data)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.default = artist.name
  form.genres.default = artist.genres.split(',')
  form.city.default = artist.city
  form.state.default = artist.state
  form.phone.default = artist.phone
  form.website.default = artist.website
  form.facebook_link.default = artist.facebook_link
  form.image_link.default = artist.image_link
  form.seeking_venue.default = artist.seeking_venue
  form.seeking_description.default = artist.seeking_description
  form.process()

  return render_template('forms/edit_artist.html', form=form, artist_id=artist_id, artist_name=artist.name)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name')
  artist.genres = ','.join(request.form.getlist('genres'))
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.website = request.form.get('website')
  artist.facebook_link = request.form.get('facebook_link')
  artist.seeking_venue = request.form.get('seeking_venue') == 'y'
  artist.seeking_description = request.form.get('seeking_description')
  artist.image_link = request.form.get('image_link')

  try:
    db.session.commit()
    flash(f'Artist {artist_id} updated succesfully!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Failed to update artist {artist_id}')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    Artist.query.filter(Artist.id==artist_id).delete()
    db.session.commit()
    flash(f'Artist {artist_id} deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Failed to delete artist {artist_id}')
  finally:
    db.session.close()

  return 'OK'


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  artist = Artist(
    name = request.form.get('name'),
    genres = ','.join(request.form.getlist('genres')),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    website = request.form.get('website'),
    facebook_link = request.form.get('facebook_link'),
    seeking_venue = request.form.get('seeking_venue') == 'y',
    seeking_description = request.form.get('seeking_description'),
    image_link = request.form.get('image_link')
  )

  try:
    db.session.add(artist)
    db.session.commit()      
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.sesion.rollback()
    flash(f'Failed to list artist {request.form["name"]}!')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():

  all_shows = Show.query.all()
  new_data = [{
    'venue_id': show.venue_id,
    'venue_name': show.venue.name,
    'artist_id': show.artist_id,
    'artist_name': show.artist.name,
    'artist_image_link': show.artist.image_link,
    'start_time': show.startTime
  }
  for show in all_shows]    

  return render_template('pages/shows.html', shows=new_data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  show = Show(
    artist_id = request.form.get('artist_id'),
    venue_id = request.form.get('venue_id'),
    startTime = datetime.strptime(request.form.get('start_time'), '%Y-%m-%d %H:%M')
  )

  try:
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Failed to list Show!')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Error handlers
#  ----------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
