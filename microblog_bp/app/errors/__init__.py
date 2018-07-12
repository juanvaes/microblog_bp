from flask import Blueprint

er = Blueprint('errors',__name__, template_folder = 'templates/errors')

from . import handlers