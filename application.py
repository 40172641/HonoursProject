from flask import Flask, render_template, request, flash, session, redirect, abort, url_for
from flask_wtf import Form
import copy
from flask_codemirror import CodeMirror
from flask_codemirror.fields import CodeMirrorField
from flask_login import LoginManager
from flask_login import current_user, login_user, login_required, UserMixin, logout_user
from wtforms import SubmitField, StringField, PasswordField, validators
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, Email, Length
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup 
from wtf_tinymce import wtf_tinymce
from wtf_tinymce.forms.fields import TinyMceField

app = Flask(__name__)
wtf_tinymce.init_app(app)
app.config['CODEMIRROR_LANGUAGES'] = ['python', 'htmlmixed']
app.config['CODEMIRROR_THEME'] = 'ambiance'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kevin/HonoursProject/database.db'
app.config['SECRET_KEY'] = 'SecretKey'
db = SQLAlchemy(app)
codemirror = CodeMirror(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    #__tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column('firstname', db.String(20), index=True)
    lastname = db.Column('lastname', db.String(20), index=True)
    email = db.Column('email', db.String(50), unique=True, index=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(20))

    def __init__(self, firstname, lastname, email, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.username = username
        self.password = password

class Lesson(db.Model):
    __tablename__ = 'lesson'
    username = db.Column('username', db.String(20), unique=True, index=True, primary_key=True)
    excercise1 = db.Column('excercise1', db.String(100))

    def __init__(self, username, excercise1):
        self.username = username
        self.excercise1 = excercise1

    def is_authenticated(self):
        return true

    def is_active(self):
        return true
    
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int (user_id)).first()

class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class RegisterForm(Form):
    firstname = StringField('Please enter your First Name', validators=[InputRequired(), Length(min=3, max=20, message='Please enter your First Name')])
    lastname = StringField('Please Enter your Last Name', validators=[InputRequired(), Length(min=3, max=20, message='Please enter your Last Name')])
    username = StringField('Please enter your Username', validators=[InputRequired(), Length(min=3, max=20)])
    email = StringField('Please enter your Email', validators=[InputRequired(), Email(message='Error')])    
    password = PasswordField('Please enter your Password', validators=[InputRequired(), Length(min=3, max=20), validators.EqualTo('confirm', message='Passwords Must Match')])
    confirm = PasswordField('Please re-enter your Password', validators=[InputRequired(), Length(min=3, max=20)])

class MyForm(Form):
    source_code = CodeMirrorField(language='python', config={'lineNumbers' : 'true'})
    body = StringField('Text', widget=TextArea(), default='Please add content')
    text = TinyMceField('My WTF TinyMCEField',tinymce_options={'toolbar': 'false', 'readonly':'1', 'height':'493', 'width':'435'})

quiz_questions = {
        'What would this Be?':['Answer1','Answer2'],
        'Test Question?!':['Answer 3','Answer 4']

}

questions = copy.deepcopy(quiz_questions)

@app.route("/")
def main():
    return render_template('main.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard', username=current_user.username))      
    form = LoginForm()   
    if request.method == 'POST' and form.validate():
        user= User.query.filter_by(username=form.username.data).first()
        if user is not None and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('.dashboard', username=user.username))
        else:
            return "Not Successful"
    return render_template('login.html', form=form)

@app.route('/register/', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard', username=current_user.username))
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        if User.query.filter_by(email=form.email.data).first():
            return 'Email already exists'
        elif User.query.filter_by(username=form.username.data).first():
            return 'Username already exists'
        else:
            user = User(form.firstname.data, form.lastname.data, form.email.data, form.username.data, form.password.data)       
            db.session.add(user)
            db.session.commit()
            return "Account Creation Successful"
    return render_template('register.html', form=form)

@app.route('/dashboard/<username>/')
@login_required
def dashboard(username):
    user = User.query.filter_by(username=username).first()
    if username != current_user.username:
        return redirect(url_for('.main'))
    return render_template('dashboard.html', user=user)


@app.route('/dashboard/<username>/template/', methods=['GET', 'POST'])
@login_required
def template(username): 
    username = User.query.filter_by(username=username).first()
    form = MyForm()
    if  Lesson.query.filter_by(username=current_user.username).scalar() is not None:
        print "User has already done this tutorial"
        loadData = Lesson.query.filter_by(username=current_user.username).first()
        #form.source_code.data = loadData.excercise1
        #form.text.data = loadData.excercise1
    if form.validate_on_submit():
        userInput = form.source_code.data
        form.text.data = userInput
        soup = BeautifulSoup(userInput)
        text = soup.text.replace('\n','')
        answer1 = "<h1>" + text + "</h1>"
        #print text
        task1 = None
        if answer1 in userInput:
            flash("Task 1 Complete")
            task1 = True
        else:
            flash("Code is incorrect")
            task1 = False
        if task1 == True:
            print "Task 1 Complete"
            lesson = Lesson(current_user.username, userInput)
            if  Lesson.query.filter_by(username=current_user.username).scalar() is None:
                db.session.add(lesson)
                db.session.commit()
            else:
                print "User Exists"
                update = Lesson.query.filter_by(username=current_user.username).first()
                update.excercise1 = userInput
                db.session.commit()
    return render_template('template.html', form=form, username=username)

@app.route('/dashboard/quiz/', methods=['GET', 'POST'])
def quizTemplate():
    if request.method == "POST":
        correct = 0
        for i in questions.keys():
            answered = request.form[i]
            if quiz_questions[i][1] == answered:
                correct = correct + 1
        return str(correct)
    return render_template('quiz.html', questions=questions)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('.main'))


@app.errorhandler(404)
def error_page(error):
    return "Couldn't find the page"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
