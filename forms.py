from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SelectField, RadioField, SubmitField, DecimalField, EmailField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from models import Category

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = RadioField('Role', choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Log In')

class AddProduct(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=100)])
    file = FileField('Product File', validators=[DataRequired()])
    price = IntegerField('Product Price', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()], coerce=int)
    add = SubmitField('Add Product')

    def __init__(self, *args, **kwargs):
        super(AddProduct, self).__init__(*args, **kwargs)
        self.category.choices = [(cat.id, cat.name) for cat in Category.query.all()]

class EditProduct(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=100)])
    file = FileField('Product File')  # FileField for product file, adjust as needed
    price = IntegerField('Product Price', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()], coerce=int)
    savechanges = SubmitField('Save Changes')

    def __init__(self, *args, **kwargs):
        super(EditProduct, self).__init__(*args, **kwargs)
        self.category.choices = [(cat.id, cat.name) for cat in Category.query.all()]