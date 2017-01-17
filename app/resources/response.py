from flask import  make_response, jsonify


def simple_response(message, key='message', status=200):
    return make_response(jsonify({key: message}), status)
