from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from .config import Config

app = Flask(__name__)
# Creates an instance of db by binding the flask application (the app object)
db = SQLAlchemy(app) 	#This is a database object
# Configurate flask object for config.py script
app.config.from_object(Config)
# Initialize a login object for the application
login = LoginManager(app)
login.login_view = 'auth.login'
# Initialize a mail application
mail = Mail(app)
#Initialize a bootstrap object
boostrap = Bootstrap(app)
#Initialize a moment object
moment = Moment(app)
# Migrates the db
migrate = Migrate(app,db)

# Register blueprints
from .main import mn
app.register_blueprint(mn, url_prefix = '/api')
from .auth import au
app.register_blueprint(au, url_prefix = '/auth')
from .errors import er
app.register_blueprint(er)

@app.route('/')
def index():
    return redirect(url_for('main.home'))

#print(app.url_map)

from . import models