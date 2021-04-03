# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from datetime import datetime
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from forms import VenueForm, ArtistForm, ShowForm
from flask_migrate import Migrate
from models import db, Venue, Artist, MusicShow

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)
db.create_all()

# DONE: connect to a local postgresql database


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/", methods=["POST", "GET", "DELETE"])
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # DONE: replace with real venues data.
    area_list = (
        db.session.query(Venue.city, Venue.state, func.count(Venue.id))
        .group_by(Venue.state, Venue.city)
        .all()
    )
    data = []
    for city, state, cnt in area_list:
        if cnt > 0:
            venue_list = Venue.query.filter(
                Venue.city == city, Venue.state == state
            ).all()
            venues = []
            for venue in venue_list:
                venues.append(
                    {
                        "id": venue.id,
                        "name": venue.name,
                    }
                )

            data.append({"city": city, "state": state, "venues": venues})

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # DONE: implement search on artists with partial string search.
    # Ensure it is case-insensitive.
    # Seach for Hop should return "The Musical Hop".
    # Search for "Music" should return "The Musical Hop"
    # and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term")
    venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
    data = []
    for venue in venues:
        data.append({"id": venue.id, "name": venue.name})

    response = {"count": len(data), "data": data}
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


def find_upcoming_shows(venue_id=None, artist_id=None):
    if venue_id is None and artist_id is None:
        return None

    upcoming_shows = []
    if venue_id is not None:
        venue = Venue.query.get(venue_id)
        music_shows = venue.shows
        now = datetime.now()
        for music_show in music_shows:
            start_time = datetime.strptime(music_show.start_time, "%Y-%m-%d %H:%M:%S")
            if start_time > now:
                upcoming_shows.append(
                    {
                        "artist_id": music_show.artist_id,
                        "artist_name": music_show.artist.name,
                        "artist_image_link": music_show.artist.image_link,
                        "start_time": music_show.start_time,
                    }
                )
    elif artist_id is not None:
        artist = Artist.query.get(artist_id)
        music_shows = artist.shows
        now = datetime.now()
        for music_show in music_shows:
            start_time = datetime.strptime(music_show.start_time, "%Y-%m-%d %H:%M:%S")
            if start_time > now:
                upcoming_shows.append(
                    {
                        "venue_id": music_show.venue_id,
                        "venue_name": music_show.venue.name,
                        "venue_image_link": music_show.venue.image_link,
                        "start_time": music_show.start_time,
                    }
                )
    return upcoming_shows


def find_past_shows(venue_id=None, artist_id=None):
    if venue_id is None and artist_id is None:
        return None

    past_shows = []
    if venue_id is not None:
        venue = Venue.query.get(venue_id)
        music_shows = venue.shows
        now = datetime.now()
        for music_show in music_shows:
            start_time = datetime.strptime(music_show.start_time, "%Y-%m-%d %H:%M:%S")
            if start_time <= now:
                past_shows.append(
                    {
                        "artist_id": music_show.artist_id,
                        "artist_name": music_show.artist.name,
                        "artist_image_link": music_show.artist.image_link,
                        "start_time": music_show.start_time,
                    }
                )
    elif artist_id is not None:
        artist = Artist.query.get(artist_id)
        music_shows = artist.shows
        now = datetime.now()
        for music_show in music_shows:
            start_time = datetime.strptime(music_show.start_time, "%Y-%m-%d %H:%M:%S")
            if start_time <= now:
                past_shows.append(
                    {
                        "venue_id": music_show.venue_id,
                        "venue_name": music_show.venue.name,
                        "venue_image_link": music_show.venue.image_link,
                        "start_time": music_show.start_time,
                    }
                )
    return past_shows


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    past_shows = find_past_shows(venue_id=venue_id)
    upcoming_shows = find_upcoming_shows(venue_id=venue_id)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "seeking_talent": False,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # DONE: implement genres to take multiple string objects

    error = False
    data = {}
    try:
        # DONE: insert form data as a new Venue record in the db, instead
        req_body = request.form
        new_venue = Venue(
            name=req_body["name"],
            city=req_body["city"],
            state=req_body["state"],
            address=req_body["address"],
            phone=req_body["phone"],
            genres=req_body.getlist("genres"),
            image_link=req_body["image_link"],
            facebook_link=req_body["facebook_link"],
        )
        db.session.add(new_venue)
        db.session.commit()

        data["name"] = new_venue.name
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        # DONE: modify data to be the data object returned from db insertion
        # DONE: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Venue " + data.name + " could not be listed.")
    else:
        # on successful db insert, flash success
        flash("Venue " + request.form["name"] + " was successfully listed!")

    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session
    # commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page,
    # have it so that clicking that button delete it from the db then
    # redirect the user to the homepage

    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # DONE: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # DONE: implement search on artists with partial string search.
    # Ensure it is case-insensitive.
    # Seach for "A" should return "Guns N Petals", "Matt Quevado",
    # and "The Wild Sax Band".
    # Search for "band" should return "The Wild Sax Band".

    search_term = request.form.get("search_term")
    artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
    data = []
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})

    response = {"count": len(data), "data": data}
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)
    past_shows = find_past_shows(artist_id=artist_id)
    upcoming_shows = find_upcoming_shows(artist_id=artist_id)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": False,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    # DONE: populate form with fields from artist with ID <artist_id>
    form = ArtistForm(obj=artist)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error = False
    try:
        req_body = request.form

        artist = Artist.query.get(artist_id)
        artist.name = req_body["name"]
        artist.city = req_body["city"]
        artist.state = req_body["state"]
        artist.phone = req_body["phone"]
        artist.genres = req_body.getlist("genres")
        artist.seeking_venue = bool(req_body["seeking_venue"])
        artist.seeking_description = req_body["seeking_description"]
        artist.image_link = req_body["image_link"]
        artist.facebook_link = req_body["facebook_link"]

        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    # DONE: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        req_body = request.form

        venue = Venue.query.get(venue_id)
        venue.name = req_body["name"]
        venue.city = req_body["city"]
        venue.state = req_body["state"]
        venue.address = req_body["address"]
        venue.phone = req_body["phone"]
        venue.genres = req_body.getlist("genres")
        venue.image_link = req_body["image_link"]
        venue.facebook_link = req_body["facebook_link"]

        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # DONE: implement genres to take multiple string objects

    error = False
    new_artist_name = "[undefined]"
    try:
        # DONE: insert form data as a new Venue record in the db, instead
        req_body = request.form
        new_artist = Artist(
            name=req_body["name"],
            city=req_body["city"],
            state=req_body["state"],
            phone=req_body["phone"],
            genres=req_body.getlist("genres"),
            seeking_venue=req_body["seeking_venue"] == "True",
            seeking_description=req_body["seeking_description"],
            image_link=req_body["image_link"],
            facebook_link=req_body["facebook_link"],
        )
        new_artist_name = new_artist.name
        db.session.add(new_artist)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        # DONE: modify data to be the data object returned from db insertion
        # DONE: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Artist " + new_artist_name + " could not be listed.")
    else:
        # on successful db insert, flash success
        flash("Artist " + new_artist_name + " was successfully listed!")

    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = MusicShow.query.all()
    data = []
    for i in range(len(shows)):
        new_show = {
            "venue_id": shows[i].venue_id,
            "venue_name": shows[i].venue.name,
            "artist_id": shows[i].artist_id,
            "artist_name": shows[i].artist.name,
            "artist_image_link": shows[i].artist.image_link,
            "start_time": shows[i].start_time,
        }
        data.append(new_show)

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead
    error = False
    req_body = request.form

    try:
        new_show = MusicShow(
            artist_id=req_body["artist_id"],
            venue_id=req_body["venue_id"],
            start_time=req_body["start_time"],
        )
        db.session.add(new_show)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        # DONE: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Show could not be listed.")
    else:
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
