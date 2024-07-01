from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'vkjbsdvkbsdjjvjkjdkjssacascacnasscnacnacnoopsokOPKOP'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MPdatabase.db'
admin_password = 'adminpass'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
