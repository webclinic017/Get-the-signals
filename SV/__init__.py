import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db_user = os.environ.get('aws_db_user')
db_pass = os.environ.get('aws_db_pass')
db_endpoint = os.environ.get('aws_db_endpoint')

app = Flask(__name__, static_url_path='/static')

# LOGIN CONFIGS
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'



# Often people will also separate these into a separate config.py file
app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
""" app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite') """

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_endpoint}:3306/flaskfinance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)


# Tell users what view to go to when they need to login.
login_manager.login_view = "login"
