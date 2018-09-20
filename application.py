from flask import Flask, render_template, request, flash, session, redirect, abort, url_for,jsonify, json
import json
import random
from flask_wtf import Form
import requests
from werkzeug.security import generate_password_hash, check_password_hash
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

class Course(db.Model):
    __tablename__ = 'course'
    courseid = db.Column(db.Integer, primary_key=True, unique=True)
    coursename = db.Column('coursename', db.String(20), index=True)
    description = db.Column('description', db.String(500), index=True)
    lessons = db.Column(db.Integer, index=True)

    def __init__(self, courseid, coursename, description, lessons):
        self.courseid = courseid
        self.coursename = coursename
        self.description = description
        self.lessons = lessons

class LessonData(db.Model):
    __tablename__ = "lessondata"
    lessonid = db.Column('lessonid', db.Integer, unique=True, index=True, primary_key=True)
    lessonname = db.Column('lessonname', db.String(30), index=True)
    lessontype = db.Column('lessontype', db.String(30), index=True)
    courseid = db.Column('courseid', db.Integer, db.ForeignKey('course.courseid'), index=True)

    def __init__(self, lessonid,lessonname, courseid):
        self.lessonid = lessonid
        self.lessonname = lessonname
        self.courseid = courseid


class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = db.Column( db.Integer, primary_key=True)
    lessonid = db.Column('lessonid', db.Integer, index=True)
    lessonname = db.Column('lessonname', db.String(30), index=True)
    courseid = db.Column('courseid', db.Integer, db.ForeignKey('course.courseid'), index=True)
    username = db.Column('username', db.String(20), index=True)
    excerciseData = db.Column('excerciseData', db.String(100))
    taskCompleted = db.Column('taskCompleted', db.String(20))

    def __init__(self, lessonid, lessonname, courseid, username, excerciseData, taskCompleted):
        self.lessonid = lessonid
        self.lessonname = lessonname
        self.courseid = courseid
        self.username = username
        self.excerciseData = excerciseData
        self.taskCompleted = taskCompleted


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
    #body = StringField('Text', widget=TextArea(), default='Please add content')
    #text = TinyMceField('My WTF TinyMCEField',tinymce_options={'toolbar': 'false', 'readonly':'1', 'height':'531', 'width':'393', 'valid_elements':'*[*]', 'allow_script_urls': 'true', 'extended_valid_elements': 'script[language|src=https://cloud.tinymce.com/stable/tinymce.min.js]'})

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
        if user is not None and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('.dashboard', username=user.username))
        else:
            flash ("Login Unsuccessful, Please Try Again")
            return redirect(url_for('.login'))
    return render_template('login.html', form=form)

@app.route('/register/', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard', username=current_user.username))
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email Already Exists")
            return redirect(url_for('.register'))
        elif User.query.filter_by(username=form.username.data).first():
            flash ('Username already exists')
            return redirect(url_for('.register'))
        else:
            user = User(form.firstname.data, form.lastname.data, form.email.data, form.username.data, generate_password_hash(form.password.data))
            print generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('.dashboard', username=user.username))
            flash ("Account Creation Successful")
    return render_template('register.html', form=form)


#This route renders the template for the Template page based on the lessonid. If the User has done this lesson before then their previous excercise data will be loaded into the text editor, however if the user has not done the lesson it will just render the standard template. Global variables are created so that they can be used an accessed by the Ajax Post, and that the user's data can be added or updated to the Database table
@app.route('/dashboard/<username>/course/<courseid>/lesson/<lessonid>')
@login_required
def template(username, courseid, lessonid):
    if username != current_user.username:
        return redirect(url_for('.dashboard', username=current_user.username))
    form = MyForm()
    with open ('lesson.json') as jsonData:
        para_data = json.load(jsonData)
    global db_courseid
    global db_lessonid
    db_courseid = courseid
    db_lessonid = lessonid
    username = User.query.filter_by(username=username).first()
    courseid = Course.query.filter_by(courseid=courseid).first()
    lessonData = LessonData.query.filter_by(lessonid=lessonid).first()
    lessonid = Lesson.query.filter_by(lessonid=lessonid).first()
    global db_lessonname
    db_lessonname = lessonData.lessonname
    global answer
    global second_answer
    if  Lesson.query.filter_by(username=current_user.username, lessonid=db_lessonid).scalar() is not None:
        print "User has already done this tutorial"
        loadData = Lesson.query.filter_by(username=current_user.username, lessonid=db_lessonid).first()
        form.source_code.data = loadData.excerciseData
    else:
        print "User has not done this tutorial"
    for json_answer in para_data:
        if json_answer['lesson_id'] == lessonData.lessonid:
            output = json_answer['answer']
            json_answer = json_answer['answer2']
            answer = str(output)
            print json_answer
            second_answer = str(json_answer)
    #print output
    for paragraph in para_data:
        #if paragraph['course_id'] == courseid.courseid:
        if paragraph['lesson_id'] == lessonData.lessonid:
            return render_template('template.html', form=form, username=username, courseid=courseid, lesson=lessonData, paragraphData=paragraph)
        #else:
         #   return render_template('template.html', form=form, username=username, courseid=courseid, lesson=lessonData, paragraphData="Example")


@app.route('/dashboard/template/post/', methods=['POST', 'GET'])
@login_required
def templatePost(): 
    form = MyForm()
    lesson = Lesson.query.filter_by(lessonid=db_lessonid).first()
    if form.validate_on_submit() and request.method == 'POST':
        userInput = form.source_code.data
        template_answer = str(answer) #Converts JSON object to String
        template_answer2 = str(second_answer) #Converts JSON object to String
        final_answer = template_answer.split() #Splits the String so the tags can be accessed for the answer
        final_answer2 = template_answer2.split()
        tag_search_answer = final_answer[0].replace("<","").replace(">","") #In order to pass a variable through soup.find, characters < & > had to be replaced
        tag_search_answer2 = final_answer2[0].replace("<","").replace(">","")
        print tag_search_answer2
        print final_answer2[0]
        soup = BeautifulSoup(userInput) #BeautifulSoup Library is used to Parse the HTML Input to find the desired user input
        task1 = None
        task2= None
        if soup.find(tag_search_answer) is None:
            print "Heading not entered"
        else:
            print "Heading Entered"
            text1 = soup.find(tag_search_answer)
            answer1 = final_answer[0] + text1.text + final_answer[1]
            if answer1 in userInput:
                task1= True
                print "Task 1 Completed"
        if soup.find(tag_search_answer2) is None:
            print "Heading not entered"
        else:
            print "Heading Entered"
            text2 = soup.find(tag_search_answer2)
            answer2 = final_answer2[0] + text2.text + final_answer2[1]
            if answer2 in userInput:
                task2= True
                print "Task 2 Completed"
        if task1 == True:
            if task2 == True:
                print "Task Complete"
                lesson = Lesson(db_lessonid, db_lessonname, db_courseid, current_user.username, userInput, "Task Completed")
                if  Lesson.query.filter_by(username=current_user.username, lessonid=db_lessonid).scalar() is None:
                    db.session.add(lesson)
                    db.session.commit()
                else:
                    print "User Exists"
                    update = Lesson.query.filter_by(username=current_user.username, lessonid = db_lessonid).first()
                    update.excerciseData = answer1
                    db.session.commit()
        return jsonify(data={'output':(form.source_code.data)})
    return jsonify(data=form.errors)

@app.route('/dashboard/<username>/')
@login_required
def dashboard(username):
    user = User.query.filter_by(username=username).first()
    if username != current_user.username:
        return redirect(url_for('.dashboard', username=current_user.username))
    return render_template('dashboard.html', user=user, courses=Course.query.all())

@app.route('/dashboard/<username>/course/<courseid>/excercise/<lessonid>/')
@login_required
def excerciseTemplate(username, courseid, lessonid):
    if username != current_user.username:
        return redirect(url_for('.dashboard', username=current_user.username))
    form = MyForm()
    username=User.query.filter_by(username=username).first()
    courseid=Course.query.filter_by(courseid=courseid).first()
    lessonData = LessonData.query.filter_by(lessonid=lessonid).first()
    return render_template('excercise.html', form=form, username=username, courseid=courseid, lesson=LessonData.query.filter_by(lessonid=lessonid, lessontype='Excercise').first())

@app.route('/dashboard/excercise/post/', methods=['POST'])
def excercise():
    form = MyForm()
    if form.validate_on_submit() and request.method == 'POST':
        userInput = form.source_code.data
        return jsonify(data={'message':(userInput)})
    return jsonify(data=form.errors)

@app.route('/dashboard/<username>/course/<courseid>/quiz/<lessonid>/', methods=['GET', 'POST'])
@login_required
def quizTemplate(username, courseid, lessonid):
    if username != current_user.username:
        return redirect(url_for('.dashboard', username=current_user.username))
    username=User.query.filter_by(username=username).first()
    courseid=Course.query.filter_by(courseid=courseid).first()
    lessonData = LessonData.query.filter_by(lessonid=lessonid).first()
    with open ('quiz.json') as jsonQuizData:
        quiz_data = json.load(jsonQuizData)
    for quiz_questions in quiz_data:
        if quiz_questions['lesson_id'] == lessonData.lessonid:
            quiz_questions = quiz_questions['quiz']
    questions = copy.deepcopy(quiz_questions)
    for j in questions:
        answer = questions[j][0]
        print answer
    for i in questions.keys():
        random.shuffle(questions[i])
    if request.method == "POST":
        correct_questions = 0
        for question in questions.keys():
            answered = request.form[question]
            if answered == answer:
                print answer
                correct_questions += 1
        return "You scored " +  str(correct_questions) + " out of 7" 
    return render_template('quiz.html', questions=questions, username=username, courseid=courseid, lesson=LessonData.query.filter_by(lessonid=lessonid, lessontype='Quiz').first())

@app.route('/dashboard/<username>/course/<courseid>/')
@login_required
def course(username, courseid):
    if username != current_user.username:
        return redirect(url_for('.dashboard', username=current_user.username))
    if Course.query.filter_by(courseid=courseid).scalar() is None:
        return render_template('error.html')
    form = MyForm()
    username = User.query.filter_by(username=username).first()
    lesson = LessonData.query.filter_by(courseid = courseid).first()
    courseid = Course.query.filter_by(courseid = courseid).first()
    return render_template('course.html', username=username, course=courseid, lessons=LessonData.query.filter_by(courseid=courseid.courseid, lessontype='Lesson'), excercises=LessonData.query.filter_by(courseid=courseid.courseid, lessontype='Excercise'), quizzes=LessonData.query.filter_by(courseid=courseid.courseid, lessontype='Quiz'))

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('.main'))

@app.route('/dashboard/')
def dashredirect():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard', username=current_user.username))
    else:
        return redirect(url_for('.main'))

@app.errorhandler(404)
def error_page(error):
    return render_template('error.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
