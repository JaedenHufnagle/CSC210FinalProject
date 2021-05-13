from flask import Flask, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import relationship
from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'traveltheworld977@gmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config ['MAIL_DEFAULT_SENDER']  =  'traveltheworld977@gmail.com'

application = app

app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)

mail= Mail(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class PostsDB(db.Model):
    __tablename__ = 'posts'
    locationInPost = db.Column(db.String, db.ForeignKey("locations.location") )
    title = db.Column(db.String(100), nullable=False, primary_key=True)
    post = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String, db.ForeignKey('users.username', ondelete='CASCADE'))

#database
class TravelDB(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(20), nullable=False, primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    child = relationship(PostsDB, backref="parent", passive_deletes=True)

#Location Database
class LocationDB(db.Model):
    __tablename__ = 'locations'
    location = db.Column(db.String(200), nullable=False, primary_key=True)
     
# this is the table for the database for the posts

db.create_all()
db.session.commit()

#Function for generating authentication keys
def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

#All that follows are forms for multiple different purposes
class PassprofileForm(FlaskForm):
    register = SubmitField('Change Password')

class submitNewName(FlaskForm):
    regi = SubmitField('Change your profile name!')

class submitNewEmail(FlaskForm):
    regis = SubmitField('Change your email!')

class PasswordForm(FlaskForm):
    old = StringField('Enter your old password:',validators=[DataRequired(),Length(max=200)])
    new = StringField('Enter your new password:',validators=[DataRequired(),Length(max=200)])
    submit= SubmitField('Update') 

class emailUpdate(FlaskForm):
    old = StringField('Enter your old email:',validators=[DataRequired(), Email(),Length(max=200)])
    new = StringField('Enter your new email:',validators=[DataRequired(), Email(),Length(max=200)])
    submit= SubmitField('Update') 

class nameUpdate(FlaskForm):
    old = StringField('Enter your old name:',validators=[DataRequired(),Length(max=200)])
    new = StringField('Enter your new name:',validators=[DataRequired(),Length(max=200)])
    submit= SubmitField('Update') 

class PostForm(FlaskForm):
    submit = SubmitField('Make a new Post!')

class PForm(FlaskForm):
    ttl = StringField('Enter the title of your post: ', validators=[DataRequired(),Length(max=100)])
    loc = StringField('What location will you be posting about? ', validators=[DataRequired()])
    post = TextAreaField('Write your post below', validators=[DataRequired(),Length(max=500)])
    submit = SubmitField('Post')

class travelForm(FlaskForm):
    userN = StringField('Username:', validators=[DataRequired()])
    passW = PasswordField('Password:', validators=[DataRequired(),Length(max=200)])
    emailN = StringField('Email:', validators=[DataRequired(),Email(),Length(max=200)])
    nameN = StringField('Name:', validators=[DataRequired(),Length(max=200)])

    submit = SubmitField('Create Profile!')

class LoginForm(FlaskForm):
    username= StringField('Username:', validators=[DataRequired(),Length(max=200)])
    password = PasswordField('Password:', validators=[DataRequired(),Length(max=200)])
    submit = SubmitField("Login")

class upForm(FlaskForm):
    update_username = StringField('update the username', validators=[DataRequired(),Length(max=200)])
    submit = SubmitField('username updated')

class passForm(FlaskForm):
    update_username = StringField('update the password', validators=[DataRequired(),Length(max=200)])
    submit = SubmitField('password updated')

class VerifyForm(FlaskForm):
    token=StringField("Enter the verification token sent to your email",validators=[DataRequired()])
    submit= SubmitField("Submit")

class ProfileDelete(FlaskForm):
    delete=SubmitField("Delete Profile")

#Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#Default route
@app.route('/')
def homepage():
    dataT = PostsDB.query.order_by(PostsDB.post)
    return render_template('homepage.html', dataT=dataT)

@app.route('/user_already_taken.html')
def al_tkn():
    return render_template('user_already_taken.html')

@app.route('/aboutus.html')
def aboutus():
    return render_template('aboutus.html')

@app.route('/signup.html', methods=['GET','POST'])
def signup():
    verify = False
    userData = None
    passData = None
    emailData = None
    nameData = None
    siup = travelForm()

    if siup.validate_on_submit():
        userData = siup.userN.data
        siup.userN.data = ''
        passData = siup.passW.data
        siup.passW.data = ''
        emailData = siup.emailN.data
        siup.emailN.data = ''
        nameData = siup.nameN.data
        siup.nameN.data = ''
        session['username']=userData
        session['password']=passData
        session['email']=emailData
        session['name']=nameData
        newUser = TravelDB(username=userData, password=passData, email=emailData, name=nameData)
        try:
            db.session.add(newUser)
            db.session.flush()
            db.session.rollback()
        except SQLAlchemyError as e:
            db.session.rollback()
            return redirect(url_for('al_tkn'))
        verif=get_random_alphanumeric_string(15)
        recipients = ['']
        recipients[0] = emailData
        msg_object = Message("Verification Code", recipients)
        msg_object.body = verif
        mail.send(msg_object)

        session['verification']=verif
        dataTable = TravelDB.query.order_by(TravelDB.username)
        return redirect(url_for('verify'))

    dataTable = TravelDB.query.order_by(TravelDB.username)
    return render_template('signup.html', siup=siup, dataTable=dataTable)

@app.route('/verify.html',methods=['Get','Post'])
def verify():
    verify=VerifyForm()
    print(session.get('verification', None))
    if verify.validate_on_submit() and verify.submit.data:
        if verify.token.data == session.get('verification', None):
            passData=session.get('password', None)
            userData=session.get('username', None)
            emailData=session.get('email',None)
            nameData= session.get('name',None)
            newUser = TravelDB(username=userData, password=passData, email=emailData, name=nameData)

            db.session.add(newUser)
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            flash("Incorrect token check again")
    return render_template('verify.html',verify=verify)

@app.route('/password.html', methods=['GET','POST'])
def passW():
    errorPresented = False
    wrong_old_pass = False
    password = PasswordForm()

    if password.validate_on_submit():
        userN = session.get('username',None)
        old_pass = password.old.data
        password.old.data = ''
        new_pass = password.new.data
        password.new.data = ''

        user_updating = TravelDB.query.get_or_404(userN)

        if user_updating.password == old_pass:
            TravelDB.query.get_or_404(userN).password = new_pass
            try:
                db.session.commit()
            except:
                errorPresented = True
                return render_template('password.html', password=password, errorPresented=errorPresented, wrong_old_pass=wrong_old_pass)

            return redirect(url_for('homepage'))

        else:
            wrong_old_pass = True
            return render_template('password.html', wrong_old_pass=wrong_old_pass, errorPresented=errorPresented, password=password)

    return render_template('password.html', wrong_old_pass=wrong_old_pass, errorPresented=errorPresented, password=password)



@app.route('/emails.html', methods=['GET','POST'])
def emails():
    errorPresented = False
    wrong_old_email = False
    emailup = emailUpdate()

    if emailup.validate_on_submit():
        userN = session.get('username',None)
        old_email = emailup.old.data
        emailup.old.data = ''
        new_email = emailup.new.data
        emailup.new.data = ''

        user_updating = TravelDB.query.get_or_404(userN)

        if user_updating.email == old_email:
            TravelDB.query.get_or_404(userN).email = new_email
            try:
                db.session.commit()
            except:
                errorPresented = True
                return render_template('emails.html', emailup=emailup, errorPresented=errorPresented, wrong_old_email=wrong_old_email)

            return redirect(url_for('homepage'))

        else:
            wrong_old_email = True
            return render_template('emails.html', wrong_old_email=wrong_old_email, errorPresented=errorPresented, emailup=emailup)

    return render_template('emails.html', wrong_old_email=wrong_old_email, errorPresented=errorPresented, emailup=emailup)

@app.route('/names.html', methods=['GET','POST'])
def names():
    errorPresented = False
    wrong_old_name = False
    nameup = nameUpdate()

    if nameup.validate_on_submit():
        userN = session.get('username',None)
        old_names = nameup.old.data
        nameup.old.data = ''
        new_name = nameup.new.data
        nameup.new.data = ''

        user_updating = TravelDB.query.get_or_404(userN)
        if user_updating.name == old_names:
            TravelDB.query.get_or_404(userN).name = new_name
            
            try:
                db.session.commit()
            except:
                errorPresented = True
                return render_template('names.html', password=password, errorPresented=errorPresented, wrong_old_name=wrong_old_name)

            return redirect(url_for('homepage'))

        else:
            wrong_old_email = True
            return render_template('names.html', wrong_old_name=wrong_old_name, errorPresented=errorPresented, nameup=nameup)

    return render_template('names.html', wrong_old_name=wrong_old_name, errorPresented=errorPresented, nameup=nameup)

@app.route('/profile.html', methods= ['GET','POST'])
def profile():
    Profile = PassprofileForm()
    Post = PostForm()
    newNam = submitNewName()
    emailup = submitNewEmail()
    Delete= ProfileDelete()
    Password=session.get('password', None)
    Username=session.get('username', None)
    Email=session.get('email',None)
    Name= session.get('name',None)

    if Post.validate_on_submit() and Post.submit.data:
        return redirect(url_for('post'))
    if Profile.validate_on_submit() and Profile.register.data:
        return redirect(url_for('passW'))
    if newNam.validate_on_submit() and newNam.regi.data:
        return redirect(url_for('names'))
    if emailup.validate_on_submit() and emailup.regis.data:
        return redirect(url_for('emails'))
    if Delete.validate_on_submit() and Delete.delete.data:
        db.session.delete(TravelDB.query.get_or_404(Username))
        result = db.session.query(PostsDB).filter(PostsDB.author==Username).all()
        for i in result:
            db.session.delete(i)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template('profile.html', Post=Post, Profile=Profile, emailup=emailup,Email=Email,Username=Username,Name=Name,Password=Password,Delete=Delete, newNam=newNam)

@app.route('/post.html',methods= ['GET','POST'])
def post():
    Post=PForm()
    information_wrong = False

    if Post.validate_on_submit(): 
        postData = Post.post.data
        Post.post.data = ''
        userN = session.get('username', None)
        passN = session.get('password', None)
        locN = Post.loc.data
        Post.loc.data = ''
        titleN = Post.ttl.data
        Post.ttl.data = ''

        user_updating = TravelDB.query.get_or_404(userN)

        if user_updating.password == passN:
            newPost = PostsDB(author=userN, post=postData, title=titleN, locationInPost=locN)
            
            try:
                db.session.add(newPost)
                db.session.commit()
            except:
                return "oh no there was a problem! :("

            dataTable = PostsDB.query.order_by(PostsDB.title)
            return redirect('/')
        else:
            information_wrong = True
            return render_template('post.html', Post=Post, information_wrong=information_wrong)
    return render_template('post.html', Post=Post, information_wrong=information_wrong)


@app.route('/signin.html',methods=['Post','Get'])
def signin():
    userData = None
    passData = None
        # emailData = None
        # nameData = None
    form = LoginForm()

    if form.validate_on_submit():
        userData = form.username.data
        passData = form.password.data            
        form.password.data = ''
        session['username']=userData
        session['password']=passData
        Name=TravelDB.query.get_or_404(userData).name
        Email=TravelDB.query.get_or_404(userData).email
        Password=TravelDB.query.get_or_404(userData).password
        print(Password)
        if Name is None or passData!=Password:
            flash('Incorrect Password or Username Please Try again')
            # emailData = form.emailN.data
            # form.emailN.data = ''
            # nameData = form.nameN.data
            # form.nameN.data = ''
        else:
            session['email']=Email
            session['name']=Name
            return redirect(url_for('profile'))
    #         # newUser = TravelDB(username=userData, password=passData, email=emailData, name=nameData)
    #     newUser = TravelDB(username=userData, password=passData)
    #     db.session.add(newUser)
    #     db.session.commit()
    #     dataTable = TravelDB.query.order_by(TravelDB.username)
    #         # return render_template('signin.html', form=form, userData=userData, passData=passData, newUser=newUser, email=emailData, name=nameData, dataTable=dataTable)
    #     return render_template('signin.html', form=form, userData=userData, passData=passData, newUser=newUser, dataTable=dataTable)

    # dataTable = TravelDB.query.order_by(TravelDB.username)
    #     # return render_template('signin.html', form=form, userData=userData, passData=passData, email=emailData, name=nameData, dataTable=dataTable)
    return render_template('signin.html', form=form)
