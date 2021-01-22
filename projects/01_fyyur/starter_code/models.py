from starter_code.app import db
from datetime import datetime
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=True)

    website = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship('Show', backref=db.backref('venue', cascade='all,  delete'))

    def __repr__(self):
      return f'Venue {self.id}: {self.name} @ {self.city}, {self.state}'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=True)

    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship('Show', backref=db.backref('artist', cascade='all, delete'))

    def __repr__(self):
      return f'Arist {self.id}: {self.name} @ {self.city}, {self.state}'


class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'))
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'))
  startTime = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'Show {self.id}: {self.artist.name} @ {self.venue.name} on {self.startTime.strftime("%Y-%m-%d %H:%M")}'


Artist.num_upcoming_shows = db.column_property(
  db.select([db.func.count(Show.id)]).\
    where(Show.artist_id==Artist.id).where(Show.startTime > datetime.now())
)

Venue.num_upcoming_shows = db.column_property(
  db.select([db.func.count(Show.id)]).\
    where(Show.venue_id==Venue.id).where(Show.startTime > datetime.now())
)
