from config import app_config
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def load_models():
    """
    load the models
    """
    from app.user import model as user_model
    from app.building import model as building_model
    from app.room import model as room_model
    from app.note import model as note_model
    from app.university import model as university_model


def register_blueprints(app):
    """
    set up the apis
    """
    #try url_prefix='/api'...
    from app.user.api import user_blueprint
    from app.room.api import room_blueprint
    from app.building.api import building_blueprint
    from app.note.api import note_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/api')
    app.register_blueprint(room_blueprint, url_prefix='/api')
    app.register_blueprint(building_blueprint, url_prefix='/api')
    app.register_blueprint(note_blueprint, url_prefix='/api')


def create_app(config_name='development'):
    """
    create the app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    migrate = Migrate(app, db)
    load_models()
    register_blueprints(app)
    return app

