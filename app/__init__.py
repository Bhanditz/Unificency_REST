from config import app_config
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def load_models():
    """
    load the models
    """
    from app.group import model as group_model
    from app.note import model as note_model
    from app.user import model as user_model_
    from app.building import model as building_model
    from app.room import model as room_model
    from app.university import model as university_model


def register_blueprints(app):
    """
    set up the apis
    """
    #try url_prefix='/api'...
    from app.user.api import user_blueprint
    from app.validation.auth import auth_blueprint
    from app.room.api import room_blueprint
    from app.building.api import building_blueprint
    from app.note.api import note_blueprint
    from app.group.api import group_blueprint
    from app.university.api import university_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api')
    app.register_blueprint(group_blueprint, url_prefix='/api')
    app.register_blueprint(user_blueprint, url_prefix='/api')
    app.register_blueprint(room_blueprint, url_prefix='/api')
    app.register_blueprint(building_blueprint, url_prefix='/api')
    app.register_blueprint(note_blueprint, url_prefix='/api')
    app.register_blueprint(university_blueprint, url_prefix='/api')


def create_app(config_name='production'):
    """
    create the app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    #app.url_map.strict_slashes = False
    db.init_app(app)
    migrate = Migrate(app, db)
    load_models()
    register_blueprints(app)
    return app

