from flask import Flask, request, render_template, request, redirect, url_for, current_app as app, session
from sqlalchemy import or_
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies
from application.models import *
from flask import Flask, session
from flask_restful import Api, Resource, reqparse
from flask import jsonify
from datetime import datetime


class HomeResource(Resource):
    def get(self):
        if "user" in session:
            if session["user"].startswith("admin"):
                return {"redirect": url_for("admin")}
            return {"redirect": url_for("userHome")}
        return {"message": "Welcome to the home page"}

home_resource = HomeResource()

class UserLoginResource(Resource):
    def get(self):
        # Read the login page HTML file and return it
        with open("path_to_login_page.html", "r") as file:
            login_page_html = file.read()
        return login_page_html

class UserLoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("password", type=str, required=True, help="Password is required")
        args = parser.parse_args()

        user = args["username"]
        password = args["password"]

        user_query = Users.query.filter_by(userName=user).first()
        if user_query is None:
            return {"error": "Invalid username or password"}

        db_password = user_query.password
        if db_password != password:
            return {"error": "Invalid username or password"}
        
        user_db = Users.query.filter_by(userName=user).first()
        user_db.lastAct = datetime.now().replace(microsecond=0)
        db.session.commit()

        # Generate an access token
        access_token = create_access_token(identity=user)

        response = {"message": "Login successful", "access_token": access_token}

        # Set the SameSite attribute for the access token cookie
        if 'access_token_cookie' in request.cookies:
            response = unset_jwt_cookies(response)

        return response
    def get(self):
        if "user" in session:
            return {"message": "User already logged in"}
        return {"message": "Please log in"}

user_login_resource = UserLoginResource()

class AdminLoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("password", type=str, required=True, help="Password is required")
        args = parser.parse_args()

        user = args["username"]
        password = args["password"]

        user_query = Users.query.filter_by(userName=user).first()
        if user_query is None or not user.startswith("admin"):
            return {"error": "Invalid username or password"}

        db_password = user_query.password
        if db_password != password:
            return {"error": "Invalid username or password"}

        # Generate an access token
        access_token = create_access_token(identity=user)

        response = {"message": "Login successful", "access_token": access_token}

        # Set the SameSite attribute for the access token cookie
        if 'access_token_cookie' in request.cookies:
            response = unset_jwt_cookies(response)

        return response

    def get(self):
        if "user" in session:
            return {"redirect": url_for("admin")}
        return {"message": "Please log in"}

admin_login_resource = AdminLoginResource()

class SignupResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("password", type=str, required=True, help="Password is required")
        args = parser.parse_args()

        user = args["username"]
        password = args["password"]

        # Check if the user already exists in the database
        user_exists = Users.query.filter_by(userName=user).first()
        if user_exists:
            return {"error": "User already exists"}

        # Insert the new user into the database
        new_user = Users(userName=user, password=password, lastAct=datetime.now().replace(microsecond=0))
        db.session.add(new_user)
        db.session.commit()
        return {"message": "SignUp successful"}

    def get(self):
        return {"message": "Please sign up"}

signup_resource = SignupResource()

class LogoutResource(Resource):
    def get(self):
        session.clear()
        return {"redirect": url_for("home")}

logout_resource = LogoutResource()


# --------------------------------------------------------ADMIN ROUTES----------------------------------------------------------------------------


class AdminHomeResource(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        
        # Check if the user has the admin role
        if user.startswith("admin"):
            return {"message": "Admin Home"}
        else:
            return {"message": "Unauthorized access"}, 403

admin_home_resource = AdminHomeResource()

class AddTheatreResource(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()

        # Check if the user has the admin role
        if user.startswith("admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("theatreName", type=str, required=True, help="Theatre name is required")
            parser.add_argument("theatreLocation", type=str, required=True, help="Theatre location is required")
            args = parser.parse_args()

            theatreName = args["theatreName"]
            theatreLocation = args["theatreLocation"]

            existing_theatre = Theatres.query.filter_by(theatreName=theatreName).first()
            if not existing_theatre:
                new_theatre = Theatres(theatreName=theatreName, location=theatreLocation)
                db.session.add(new_theatre)
                db.session.commit()
                return {"message": "Theatre Added Successfully"}

            return {"message": "Theatre already exists"}
        else:
            return {"message": "Unauthorized access"}, 403

    def get(self):
        return {"message": "Add a new theatre"}

add_theatre_resource = AddTheatreResource()

class MoviesResource(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()  # Get the current user from the JWT token

        # Check if the user has the admin role
        if user.startswith("admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("PresentMovieName", type=str, required=False)
            parser.add_argument("NewMovieName", type=str, required=False)
            parser.add_argument("MovieNameToDelete", type=str, required=False)
            args = parser.parse_args()

            if args["PresentMovieName"] and args["NewMovieName"]:
                # Update movie name
                oldMovieName = args["PresentMovieName"]
                modifiedMovieName = args["NewMovieName"]
                movie_to_update = Movies.query.filter_by(movieName=oldMovieName).first()
                if movie_to_update:
                    movie_to_update.movieName = modifiedMovieName
                    db.session.commit()
                    return {"message": "Movie name updated"}

            elif args["MovieNameToDelete"]:
                # Delete movie
                deleteMovieName = args["MovieNameToDelete"]
                movie_to_delete = Movies.query.filter_by(movieName=deleteMovieName).first()
                if movie_to_delete:
                    db.session.delete(movie_to_delete)
                    db.session.commit()
                    return {"message": "Movie deleted"}

            return {"message": "Invalid request"}
        else:
            return {"message": "Unauthorized access"}, 403

    def get(self):
        r = db.session.query(
            MovieShowings.movieShowingID,
            MovieShowings.showCapacity,
            Movies.movieName,
            MovieDates.movieDate,
            MovieTimes.movieTime
        ).join(
            Movies,
            MovieShowings.movieID == Movies.movieID
        ).join(
            MovieDates,
            MovieShowings.movieDateID == MovieDates.movieDateID
        ).join(
            MovieTimes,
            MovieShowings.movieTimeID == MovieTimes.movieTimeID
        ).all()

        # Convert the query results to a list of dictionaries (serialized format)
        rows = []
        for row in r:
            rows.append({
                "movieShowingID": row.movieShowingID,
                "showCapacity": row.showCapacity,
                "movieName": row.movieName,
                "movieDate": row.movieDate,
                "movieTime": row.movieTime
            })

        # Return the serialized data in a JSON response
        return jsonify({"rows": rows})

movies_resource = MoviesResource()

class TheatresResource(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()  # Get the current user from the JWT token

        # Check if the user has the admin role
        if user.startswith("admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("PresentTheatreName", type=str, required=False)
            parser.add_argument("NewTheatreName", type=str, required=False)
            parser.add_argument("TheatreNameToDelete", type=str, required=False)
            args = parser.parse_args()

            if args["PresentTheatreName"] and args["NewTheatreName"]:
                # Update theatre name
                oldTheatreName = args["PresentTheatreName"]
                modifiedTheatreName = args["NewTheatreName"]
                theatre = db.session.query(Theatres).filter(Theatres.theatreName == oldTheatreName).first()
                if theatre:
                    theatre.theatreName = modifiedTheatreName
                    db.session.commit()
                    return {"message": "Theatre name updated"}

            elif args["TheatreNameToDelete"]:
                # Delete theatre
                deleteTheatreName = args["TheatreNameToDelete"]
                theatre = db.session.query(Theatres).filter(Theatres.theatreName == deleteTheatreName).first()
                if theatre:
                    db.session.delete(theatre)
                    db.session.commit()
                    return {"message": "Theatre deleted"}

            return {"message": "Invalid request"}
        else:
            return {"message": "Unauthorized access"}, 403

    @jwt_required(optional=True)
    def get(self):
        user = get_jwt_identity()  # Get the current user from the JWT token
        theatres_data = db.session.query(Theatres.theatreID,Theatres.theatreName, Theatres.location).all()
        theatres = [{"theatreID":theatre.theatreID, "theatreName": theatre.theatreName, "location": theatre.location} for theatre in theatres_data]
        return jsonify({"rows": theatres})

theatres_resource = TheatresResource()

class AddMovieResource(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()  # Get the current user from the JWT token
        parser = reqparse.RequestParser()
        parser.add_argument("movieName", type=str, required=True)
        parser.add_argument("movieLang", type=str, required=True)
        parser.add_argument("types", type=str, required=True)
        parser.add_argument("genres", type=str, required=True)
        parser.add_argument("theatreName", type=str, required=True)
        parser.add_argument("movieDate", type=str, required=True)
        parser.add_argument("movieTime", type=str, required=True)
        parser.add_argument("showCapacity", type=int, required=True)
        args = parser.parse_args()

        movieName = args["movieName"]
        movieLang = args["movieLang"]
        types = args["types"]
        theatreName = args["theatreName"]
        movieDate = args["movieDate"]
        movieTime = args["movieTime"]
        genres = args["genres"]
        showCapacity = args["showCapacity"]

        theatre = Theatres.query.filter_by(theatreName=theatreName).first()
        if not theatre:
            return {"message": "Invalid theatre name"}

        # Inserting into Movies Table
        movie = Movies(movieName=movieName, movieLang=movieLang, types=types, genre=genres, theatreID=theatre.theatreID)
        db.session.add(movie)
        db.session.commit()

        # Inserting into MovieDates and MovieTimes Table
        movie_date = MovieDates(movieDate=movieDate, movieID=movie.movieID)
        movie_time = MovieTimes(movieTime=movieTime, movieID=movie.movieID)
        db.session.add(movie_date)
        db.session.add(movie_time)
        db.session.commit()

        # Inserting into movieShowings Table
        movieId = movie.movieID
        movieDateId = movie_date.movieDateID
        movieTimeId = movie_time.movieTimeID

        movie_showing = MovieShowings(showCapacity=showCapacity, movieID=movieId, movieDateID=movieDateId,
                                      movieTimeID=movieTimeId, theatreID=theatre.theatreID)
        db.session.add(movie_showing)
        db.session.commit()

        return {"message": "Movie added"}

    @jwt_required(optional=True)
    def get(self):
        user = get_jwt_identity()  # Get the current user from the JWT token
        theatres = Theatres.query.all()
        return jsonify({"theatres": [{"theatreName": theatre.theatreName} for theatre in theatres]})

add_movie_resource = AddMovieResource()


# ------------------------------------------------------------USER ROUTES-------------------------------------------------------------------------


class UserHomeResource(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        return {"result": username}

user_home_resource = UserHomeResource()

class UserMoviesResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('numTicketsInput', type=int)
        self.parser.add_argument('NumTicketsBooked', type=int)
        self.parser.add_argument('showIDInput', type=int)
        self.parser.add_argument('BookingMsg')

    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        rows = db.session.query(
            MovieShowings.movieShowingID,
            MovieShowings.showCapacity,
            Movies.movieName,
            Theatres.theatreName,
            MovieDates.movieDate,
            MovieTimes.movieTime
        ).join(
            Movies,
            MovieShowings.movieID == Movies.movieID
        ).join(
            MovieDates,
            MovieShowings.movieDateID == MovieDates.movieDateID
        ).join(
            MovieTimes,
            MovieShowings.movieTimeID == MovieTimes.movieTimeID
        ).join(
            Theatres,
            MovieShowings.theatreID == Theatres.theatreID
        ).all()

        # Convert the rows to a list of dictionaries
        rows_data = [
            {
                "movieShowingID": row.movieShowingID,
                "showCapacity": row.showCapacity,
                "movieName": row.movieName,
                "theatreName": row.theatreName,
                "movieDate": row.movieDate,
                "movieTime": row.movieTime,
            }
            for row in rows
        ]

        # Create a response dictionary containing the rows data
        response_data = {"rows": rows_data}
        return jsonify(response_data)

    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        args = self.parser.parse_args()
        remTickets = args['numTicketsInput']
        numTicketsBooked = args['NumTicketsBooked']
        movieShowingId = args['showIDInput']
        BookingStatus = args['BookingMsg']
        with db.session.begin():
            movie_showing = MovieShowings.query.get(movieShowingId)
            if BookingStatus == "Success":
                movie_showing.showCapacity = remTickets
                user_id = Users.query.filter_by(userName=user).first().userID
                user_booking = userBookings(userID=user_id, movieShowingID=movieShowingId, numTickets=numTicketsBooked)
                db.session.add(user_booking)
                return  {"message": "Booking processed successfully"}

        return {"message": "Booking Unsuccessfully"}

user_movies_resource = UserMoviesResource()

class UserSpecificMoviesResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('numTicketsInput', type=int)
        self.parser.add_argument('NumTicketsBooked', type=int)
        self.parser.add_argument('showIDInput', type=int)
        self.parser.add_argument('BookingMsg')

    @jwt_required()  # Requires JWT token for authentication
    def get(self,theatre):
        user = get_jwt_identity()  # Get the current user from the JWT token
        rows = db.session.query(
            MovieShowings.movieShowingID,
            MovieShowings.showCapacity,
            Movies.movieName,
            Theatres.theatreName,
            MovieDates.movieDate,
            MovieTimes.movieTime
        ).join(
            Movies,
            MovieShowings.movieID == Movies.movieID
        ).join(
            MovieDates,
            MovieShowings.movieDateID == MovieDates.movieDateID
        ).join(
            MovieTimes,
            MovieShowings.movieTimeID == MovieTimes.movieTimeID
        ).join(
            Theatres,
            MovieShowings.theatreID == Theatres.theatreID
        ).filter(
            Theatres.theatreName == theatre
        ).all()

        # Return the response as JSON using Flask jsonify
        return jsonify({"result": user, "rows": [row._asdict() for row in rows]})

    @jwt_required()  # Requires JWT token for authentication
    def post(self):
        theatre = request.view_args['theatre']
        user = get_jwt_identity()  # Get the current user from the JWT token
        args = self.parser.parse_args()
        remTickets = args['numTicketsInput']
        numTicketsBooked = args['NumTicketsBooked']
        movieShowingId = args['showIDInput']
        BookingStatus = args['BookingMsg']
        with db.session.begin():
            movie_showing = MovieShowings.query.get(movieShowingId)
            if BookingStatus == "Success":
                movie_showing.showCapacity = remTickets
                user_id = Users.query.filter_by(userName=user).first().userID
                user_booking = userBookings(userID=user_id, movieShowingID=movieShowingId, numTickets=numTicketsBooked)
                db.session.add(user_booking)

        # Return the response as JSON using Flask jsonify
        return jsonify({"message": "Booking processed successfully"})

user_specific_movies_resource = UserSpecificMoviesResource()

class UserSearch(Resource):
    @jwt_required()  # Requires JWT token for authentication
    def get(self):
        user=get_jwt_identity()
        return jsonify({"message":"Success"})

class UserSearchResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('query')
        self.parser.add_argument('numTicketsInput', type=int)
        self.parser.add_argument('NumTicketsBooked', type=int)
        self.parser.add_argument('showIDInput', type=int)
        self.parser.add_argument('BookingMsg')
    @jwt_required()
    def get(self, query):
        user = get_jwt_identity()  # Get the current user from the JWT token
        rows = db.session.query(
            MovieShowings.movieShowingID,
            MovieShowings.showCapacity,
            Movies.movieName,
            Theatres.theatreName,
            MovieDates.movieDate,
            MovieTimes.movieTime,
            Movies.types,
            Movies.genre,
            Movies.movieLang,
            Theatres.location
        ).join(
            Movies,
            Movies.movieID == MovieShowings.movieID
        ).join(
            MovieDates,
            MovieDates.movieDateID == MovieShowings.movieDateID
        ).join(
            MovieTimes,
            MovieTimes.movieTimeID == MovieShowings.movieTimeID
        ).join(
            Theatres,
            Theatres.theatreID == MovieShowings.theatreID
        ).filter(
            or_(
                Movies.movieName.like(f"%{query}%"),
                Theatres.theatreName.like(f"%{query}%"),
                Movies.genre.like(f"%{query}%"),
                Theatres.location.like(f"%{query}%"),
                Movies.movieLang.like(f"%{query}%"),
                Movies.types.like(f"%{query}%")
            )
        ).all()

        # Return the response as JSON using Flask jsonify
        return jsonify({"result": user, "rows": [row._asdict() for row in rows]})
    
user_search_resource = UserSearchResource()

class UserTheatresResource(Resource):
    @jwt_required()  # Requires a valid JWT token to access this endpoint
    def get(self):
        user = get_jwt_identity()  # Get the current user from the JWT token
        theatres = Theatres.query.all()
        rows_data = [
            {
                "theatreID": row.theatreID,
                "theatreName": row.theatreName,
                "location": row.location,
            }
            for row in theatres
        ]
        # Create a response dictionary containing the rows data
        response_data = {"rows": rows_data}
        return jsonify(response_data)

user_theatres_resource = UserTheatresResource()

class UserBookingsResource(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        user_id = Users.query.filter_by(userName=user).first().userID

        rows = db.session.query(
            Users.userID,
            userBookings.bookingID,
            Movies.movieName,
            Theatres.theatreName,
            MovieDates.movieDate,
            MovieTimes.movieTime,
            userBookings.numTickets
        ).join(
            MovieShowings,
            MovieShowings.movieShowingID == userBookings.movieShowingID,
        ).join(
            Movies,
            Movies.movieID == MovieShowings.movieID
        ).join(
            MovieDates,
            MovieDates.movieDateID == MovieShowings.movieDateID
        ).join(
            MovieTimes,
            MovieTimes.movieTimeID == MovieShowings.movieTimeID
        ).join(
            Theatres,
            Theatres.theatreID == MovieShowings.theatreID
        ).filter(
            userBookings.userID == user_id,
            Users.userID == user_id
        ).all()

        return jsonify({"result": user, "rows": [row._asdict() for row in rows]})


def register_resources(api):
    api.add_resource(LogoutResource, "/logout")
    api.add_resource(SignupResource, "/signup")
    api.add_resource(AdminLoginResource, "/adminlogin")
    api.add_resource(UserLoginResource, "/userlogin")
    api.add_resource(HomeResource, "/")
    api.add_resource(UserBookingsResource, "/user/bookings")
    api.add_resource(UserSearchResource,"/user/search/<string:query>")
    api.add_resource(UserSearch,"/user/search")
    api.add_resource(UserSpecificMoviesResource, "/user/<string:theatre>/movies")
    api.add_resource(UserMoviesResource, "/user/movies")
    api.add_resource(UserTheatresResource, "/user/theatres")
    api.add_resource(UserHomeResource, "/user/home")
    api.add_resource(AddMovieResource, "/admin/addMovie")
    api.add_resource(AdminHomeResource, "/admin/home")
    api.add_resource(AddTheatreResource, "/admin/addTheatre")
    api.add_resource(TheatresResource, "/admin/theatres")
    api.add_resource(MoviesResource, "/admin/movies")
    