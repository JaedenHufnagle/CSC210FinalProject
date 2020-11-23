from flask import Flask, render_template,request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
application = app
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///ingredients.db'

db=SQLAlchemy(app)

migrate = Migrate(app, db)

class Ingredients(db.Model):
    _tablename_='ingredients'
    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String(200),nullable=False)

    def _repr_ (self):
        return '<Ingredient %r>' % self.ingredient

bootstrap = Bootstrap(app)
moment = Moment(app)



@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Ingredients=Ingredients)

class ItemForm(FlaskForm):
    item = StringField('Add a new item:', validators=[DataRequired()])
    submit = SubmitField('Add Item!')

class DeleteForm(FlaskForm):
    item = StringField('Enter the item you wish to delete', validators=[DataRequired()])
    submit = SubmitField('Remove item')

class EditForm(FlaskForm):
    inital = StringField('Enter the item you wish to change', validators=[DataRequired()])
    change = StringField('Enter the items new information', validators=[DataRequired()])
    submit = SubmitField('Change item')

class ModeForm(FlaskForm):
    options=[('edit','Edit Mode'),('delete','Delete Mode'), ('add','Add Mode')]
    mode = SelectField(u'View', choices=options)
    submit = SubmitField('Change Mode')

class EmptyForm(FlaskForm):
    empty= StringField('Click one of the modes above to get started')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/add',methods= ['GET','POST'])
def add_index():
    form = ItemForm()
    mode = ModeForm()

    
    if mode.is_submitted():
        if(mode.mode.data=='delete'):
             return redirect(url_for('delete_index'))
        elif(mode.mode.data=='add'):
            return redirect(url_for('add_index'))
        elif(mode.mode.data=='edit'):
            return redirect(url_for('edit_index'))

    if form.is_submitted():
        ingredient = Ingredients.query.filter_by(ingredient=form.item.data).first()
        if ingredient is None:
            ingredient= Ingredients(ingredient=form.item.data)
            db.session.add(ingredient)
            db.session.commit()

    form.item.data=None
    ingredients=db.session.query(Ingredients).filter_by().all()
    return render_template('index.html' ,Ingredients=ingredients, form=form,mode=mode)

@app.route('/edit',methods= ['GET','POST'])
def edit_index():
    form=EditForm()
    mode = ModeForm()

    
    if mode.is_submitted():
        if(mode.mode.data=='delete'):
             return redirect(url_for('delete_index'))
        elif(mode.mode.data=='add'):
            return redirect(url_for('add_index'))
        elif(mode.mode.data=='edit'):
            return redirect(url_for('edit_index'))

    if form.is_submitted():
        initial=form.inital.data
        result=db.session.query(Ingredients).filter_by(ingredient=initial).first()
        if result is not None:
            db.session.delete(result)
            change=form.change.data
            ingredient=Ingredients(ingredient=change)
            db.session.add(ingredient)
            db.session.commit()

    form.change.data=None
    form.inital.data=None
    ingredients=db.session.query(Ingredients).filter_by().all()

    return render_template('index.html' ,Ingredients=ingredients, form=form, mode=mode)


@app.route('/delete',methods=['GET','POST'])
def delete_index():
    form = DeleteForm()
    mode = ModeForm()

    
    if mode.is_submitted():
        if(mode.mode.data=='delete'):
             return redirect(url_for('delete_index'))
        elif(mode.mode.data=='add'):
            return redirect(url_for('add_index'))
        elif(mode.mode.data=='edit'):
            return redirect(url_for('edit_index'))

    if form.is_submitted():
        result=db.session.query(Ingredients).filter_by(ingredient=form.item.data).first()
        if result is not None:
            db.session.delete(result)
            db.session.commit()
            
    form.item.data=None
    ingredients=db.session.query(Ingredients).filter_by().all()
    return render_template('index.html', Ingredients=ingredients,form=form, mode=mode)



@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmptyForm()
    mode = ModeForm()

    if mode.is_submitted():
        if(mode.mode.data=='delete'):
             return redirect(url_for('delete_index'))
        elif(mode.mode.data=='add'):
            return redirect(url_for('add_index'))
        elif(mode.mode.data=='edit'):
            return redirect(url_for('edit_index'))


    ingredients=db.session.query(Ingredients).filter_by().all()

    return render_template('index.html', Ingredients=ingredients, mode=mode, form=form)
