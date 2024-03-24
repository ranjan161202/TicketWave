import os
from flask import Flask, request,jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from application.controllers import register_resources
from flask_cors import CORS
# from celery.schedules import crontab
# from cache_config import make_cache
# import tasks

app = None
api = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "raghavraoghanathe"
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)

    # Configure JWT
    jwt = JWTManager(app)
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']  # Set the expected token locations
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'  # Specify the cookie path (adjust as needed)
    app.config['JWT_COOKIE_SAMESITE'] = 'None'
    db.init_app(app)

    # Use CORS to enable Cross-Origin Resource Sharing
    CORS(app)

    return app

app = create_app()
app.app_context().push()
api = Api(app)

# cache = make_cache(app)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_BACKEND'] = 'redis://localhost:6379/0'

# from celery_config import make_celery
# celery = make_celery(app)


@app.route('/admin/<int:tid>', methods=['POST'])
@jwt_required()
def exportTheatre(tid):
    # tasks.exTheatre.delay(tid)
    return jsonify('Task submitted')

# Register your API resources
register_resources(api)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)