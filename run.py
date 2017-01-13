import os
from app import create_app
from flask_restful import Resource, Api

config_name = os.getenv('FLASK_CONFIG')
app = create_app('production')


if __name__ == '__main__':
    app.run()

