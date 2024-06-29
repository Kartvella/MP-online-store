from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'vkjbsdvkbsdjjvjkjdkjssacascacnasscnacnacnoopsokOPKOP'
UPLOAD_FOLDER = r'C:\Users\kartv\OneDrive\Desktop\Final Project\static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MPdatabase.db'
admin_password = 'adminpass'
db = SQLAlchemy(app)

login_manager = LoginManager(app)