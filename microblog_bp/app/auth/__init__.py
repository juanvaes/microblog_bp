from flask import Blueprint

au = Blueprint('auth', __name__, template_folder='templates/auth')

from . import views