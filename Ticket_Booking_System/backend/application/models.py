from .database import db

class Movies(db.Model):
    __tablename__ = 'Movies'
    movieID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    movieName = db.Column(db.String, nullable=False)
    movieLang = db.Column(db.String)
    types = db.Column(db.String)
    genre = db.Column(db.String)
    theatreID = db.Column(db.Integer,db.ForeignKey("Theatres.theatreID",ondelete='CASCADE'))
    theatre = db.relationship('Theatres', backref=db.backref('movies', cascade='all, delete-orphan'))

class Theatres(db.Model):
    __tablename__ = 'Theatres'
    theatreID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    theatreName = db.Column(db.String, nullable=False)
    location = db.Column(db.String)

class MovieDates(db.Model):
    __tablename__ = 'MovieDates'
    movieDateID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    movieDate = db.Column(db.String, nullable=False)
    movieID = db.Column(db.Integer,db.ForeignKey("Movies.movieID",ondelete='CASCADE'))
    MovieDateMovies = db.relationship('Movies', backref=db.backref('MovieDates', cascade='all, delete-orphan'))


class MovieTimes(db.Model):
    __tablename__ = 'MovieTimes'
    movieTimeID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    movieTime = db.Column(db.String, nullable=False)
    movieID = db.Column(db.Integer,db.ForeignKey("Movies.movieID",ondelete='CASCADE'))
    MovieTimeMovies = db.relationship('Movies', backref=db.backref('MovieTimes', cascade='all, delete-orphan'))


class MovieShowings(db.Model):
    __tablename__ = 'MovieShowings'
    movieShowingID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    showCapacity = db.Column(db.Integer, nullable=False)
    movieID = db.Column(db.Integer,db.ForeignKey("Movies.movieID",ondelete='CASCADE'))
    movieDateID = db.Column(db.Integer,db.ForeignKey("MovieDates.movieDateID"))
    movieTimeID = db.Column(db.Integer,db.ForeignKey("MovieTimes.movieTimeID"))
    theatreID = db.Column(db.Integer,db.ForeignKey("Theatres.theatreID",ondelete='CASCADE'))
    MovieShowTheatre = db.relationship('Theatres', backref=db.backref('MovieShowings', cascade='all, delete-orphan'))
    MovieShowMovie = db.relationship('Movies', backref=db.backref('MovieShowings', cascade='all, delete-orphan'))

class Users(db.Model):
    __tablename__ = 'Users'
    userID = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    userName = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    lastAct = db.Column(db.String)

class userBookings(db.Model):
    __tablename__ = 'userBookings'
    bookingID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    numTickets = db.Column(db.Integer, nullable=False)
    userID = db.Column(db.Integer,db.ForeignKey("Users.userID",ondelete='CASCADE'))
    movieShowingID = db.Column(db.Integer,db.ForeignKey("MovieShowings.movieShowingID",ondelete='CASCADE'))
    userBookMovShow = db.relationship('MovieShowings', backref=db.backref('userBookings', cascade='all, delete-orphan'), foreign_keys=[movieShowingID])
