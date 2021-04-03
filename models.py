from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MusicShow(db.Model):
    __tablename__ = "music_show"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    start_time = db.Column(db.String(120))

    def __repr__(self):
        return "<MusicShow: {}, {}, {}, {}>".format(
            self.id, self.artist_id, self.venue_id, self.start_time
        )


class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())

    shows = db.relationship("MusicShow", backref="venue", lazy=True)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return "<Venue: {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id,
            self.name,
            self.city,
            self.state,
            self.address,
            self.phone,
            self.genres,
            self.image_link,
            self.facebook_link,
        )


# DONE: Implement Show and Artist models, and complete all model relationships and
#       properties, as a database migration.
class Artist(db.Model):
    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("MusicShow", backref="artist", lazy=True)

    def __repr__(self):
        return "<Artist: {}, {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id,
            self.name,
            self.city,
            self.state,
            self.phone,
            self.genres,
            self.seeking_venue,
            self.seeking_description,
            self.image_link,
            self.facebook_link,
        )
