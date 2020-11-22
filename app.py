from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


#class NameForm(FlaskForm):
    #ingredient = StringField('Enter a new item?', validators=[DataRequired()])
    #submit = SubmitField('Add it!')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def homepage():
    #ingredient = None
    #form = NameForm()
    #if form.validate_on_submit():
       # ingredient = form.ingredient.data
       # form.ingredient.data = ''
    return render_template('homepage.html')