import os
import response
import config
import os
from werkzeug.utils import secure_filename
from flask import request
import random
import string
import config


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.Config().ALLOWED_EXTENSIONS


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_uploaded_image_and_save(save_to,**kwargs):
    if 'file' not in request.files:
        return response.simple('You have to provide a file', 404)
    file = request.files['file']
    if not file:
        response.simple_response('no file', 404)
    if file.filename == '':
        return response.simple('Empty file', 404)
    if not allowed_file(file.filename):
        return response.simple_response('this kind of data is not allowed', 400)
    filename = secure_filename(file.filename)
    new_filename = kwargs.get('rename_to')
    if new_filename:
        _, file_extension = os.path.splitext(filename)
        filename = new_filename + file_extension
    path = os.path.join(save_to, filename)
    while os.path.isfile(os.path.join(config.Config().PROJECT_ROOT, path)):
        filename, file_extension = os.path.splitext(path)
        path = os.path.join(save_to,  id_generator()+file_extension)
    file.save(os.path.join(config.Config().PROJECT_ROOT, path))
    return path


def delete_if_exists(path):
    if(os.path.isfile(path)):
        os.remove(path)
        return True
    else:
        return False
