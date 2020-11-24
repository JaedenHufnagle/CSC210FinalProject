from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms import validators
from wtforms.validators import Required
from wtforms.fields.html5 import EmailField, DateTimeLocalField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class ProfileForm(FlaskForm):
    name = StringField('Name:', validators=[validators.DataRequired()])
    username = StringField('Username:', validators=[validators.DataRequired()])
    email = EmailField('Email:', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password:')
    submit = SubmitField('Sign up')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/signup')
def singup():
    form = ProfileForm()
    #ingredient = None
    #form = NameForm()
    #if form.validate_on_submit():
       # ingredient = form.ingredient.data
       # form.ingredient.data = ''
    return render_template('signup.html',form=form)