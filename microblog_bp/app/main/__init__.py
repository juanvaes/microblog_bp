from flask import Blueprint

mn = Blueprint('main',__name__, template_folder='templates/main')

from . import views