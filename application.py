from flask import Flask, render_template, request, flash, session, redirect, abort, url_for,jsonify, json
import json
import random
from flask_wtf import Form
import requests
import difflib
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
    __tablename__ = 'user'
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

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    lessonid = db.Column('lessonid', db.Integer, index=True)
    courseid = db.Column('courseid', db.Integer, db.ForeignKey('course.courseid'), index=True)
    username = db.Column('username', db.String(20), index=True)
    quizscore = db.Column('quizscore', db.Integer, index=True)
    feedback = db.Column('feedback', db.String(100))

    def __init__(self, lessonid, courseid, username, quizscore, feedback):
        self.lessonid = lessonid
        self.courseid = courseid
        self.username = username
        self.quizscore = quizscore
        self.feedback = feedback

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
    with open ('static/lesson/lesson.json') as jsonData:
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
    global feedback
    global feedback2
    global incorrect_feedback
    global incorrect_feedback2
    if  Lesson.query.filter_by(username=current_user.username, lessonid=db_lessonid).scalar() is not None:
        print "User has already done this tutorial"
        loadData = Lesson.query.filter_by(username=current_user.username, lessonid=db_lessonid).first()
        form.source_code.data = loadData.excerciseData
    else:
        print "User has not done this tutorial"
    for json_answer in para_data:
        if json_answer['lesson_id'] == lessonData.lessonid:
            json_feedback = json_answer['feedback']
            json_feedback_Q2 = json_answer['feedback2']
            json_incorrect = json_answer['incorrect_feedback']
            json_incorrect_Q2 = json_answer['incorrect_feedback2']
            output = json_answer['answer']
            json_answer = json_answer['answer2']
            answer = str(output)
            feedback = str(json_feedback)
            feedback2 = str(json_feedback_Q2)
            incorrect_feedback = str(json_incorrect)
            incorrect_feedback2 = str(json_incorrect_Q2)
            print json_answer
            second_answer = str(json_answer)
    #print output
    for paragraph in para_data:
        #if paragraph['course_id'] == courseid.courseid:
        if paragraph['lesson_id'] == lessonData.lessonid:
            return render_template('template.html', form=form, username=username, courseid=courseid, lesson=lessonData, paragraphData=paragraph)
        #else:
         #   return render_template('template.html', form=form, username=username, courseid=courseid, lesson=lessonData, paragraphData="Example")

#For AJAX POST requests to work in flask, they have to split into two routes. The information in this route including the users form data is converted to a JSON which is sent to the templated lesson page. The JSON from this route is then displayed on the templated lesson page through JQuery. This route was created by essentially splitting the functionality of the initial template lesson page which used a simple redirect to run the code into two different routes so AJAX would work.
@app.route('/dashboard/template/post/', methods=['POST'])
@login_required
def templatePost(): 
    form = MyForm()
    lesson = Lesson.query.filter_by(lessonid=db_lessonid).first()
    if form.validate_on_submit() and request.method == 'POST':
        userInput = form.source_code.data
        template_answer = str(answer) #Converts JSON object to String
        template_answer2 = str(second_answer) #Converts JSON object to String
        user_feedback = str(feedback)
        user_feedback_Q2 = str(feedback2)
        user_incorrect_feedback = str(incorrect_feedback)
        user_incorrect_feedbackQ2 = str(incorrect_feedback2)
        #Although the global variables were cast as strings in the route above, I was getting errors when trying to use them. The fix was casting them a second time and assigning them to another variable
        final_answer = template_answer.split() #Splits the String so the tags can be accessed for the answer
        final_answer2 = template_answer2.split() #Splits the String so the tags can be accessed for the answer
        print len(final_answer)
        non_tag_array = [] #Array to store all of the heading with the removal of tags for the soup.find functionality
        tag_array = [] 
        non_tag_array_A2 = []
        tag_array_A2 = []
        if len(final_answer) > 2:
            for x in final_answer:
                if "/" not in x:
                    tag_array.append(x)
                    array = x.replace("<","").replace(">","")
                    non_tag_array.append(array)
        if len(final_answer2) > 2:
            for x in final_answer2:
                if "/" not in x:
                    tag_array_A2.append(x)
                    array = x.replace("<","").replace(">","")
                    non_tag_array_A2.append(array)
        #For the beatiful soup library to scrape through the HTML, the tags must have <> removed. These values are then appended into an array for the answers which have more than one HTML element as the correct answer. The if statement ensures it only appends opening tags and not closing 
        tag_search_answer = final_answer[0].replace("<","").replace(">","") #In order to pass a variable through soup.find, characters < & > had to be replaced
        tag_search_answer2 = final_answer2[0].replace("<","").replace(">","")
        soup = BeautifulSoup(userInput, 'html.parser') #BeautifulSoup Library is used to Parse the HTML Input to find the desired user input
        task1 = None
        task2 = None
        if len(final_answer) > 2:
            if not all(soup.find(tag) for tag in (non_tag_array)):
                print "Did not enter headings"
                task1 = False
            else:
                print "Heading Entered"
                find_answer = soup.find(non_tag_array)
                answer1 = str(find_answer)
                task1 = True
                print answer1
                print userInput
        if len(final_answer2) > 2:
            if not all(soup.find(tag) for tag in (non_tag_array_A2)):
                print "Did not enter headings"
                task2 = False
            else:
                print "Heading Entered"
                find_answer = soup.find(non_tag_array_A2)
                answer2 = str(find_answer)
                task2 = True
                print answer2
                print userInput
        #The search through the headings aspect of the beautiful soup functionality for returning false values for not matching all of the headings in the heading array because the code would not display without it.
        if len(final_answer) == 2:
            if soup.find(tag_search_answer) is None:
                print "Heading not entered"
                task1 = False
            else:
                print "Heading Entered"
                text1 = soup.find(tag_search_answer)
                answer1 = final_answer[0] + text1.text + final_answer[1]
                if answer1 in userInput:
                    task1= True
                    print "Task 1 Completed"
                else:
                    task1 = False
                    print "Task 1 Incomplete" 
        if len(final_answer2) == 2:
            if soup.find(tag_search_answer2) is None:
                print "Heading not entered"
                task2=False
            else:
                print "Heading Entered"
                text2 = soup.find(tag_search_answer2)
                answer2 = final_answer2[0] + text2.text + final_answer2[1]
            #print answer2
                if answer2 in userInput:
                    task2= True
                    print "Task 2 Completed"
                else:
                    task2 = False
        #This is the Datbase functionality, if both the tasks are true, The users entry is added to the DB, however first there's a check to see if the user already has a DB entry for that lesson. If they don't an entry is created, if they do then their entry is updated with the code they have just entered
        #It was initially programmed simpler, with less nested if statements, however for user feedback functionality, feedback has to be returned to the user whether both tasks are completed, only one is, or none are. This is done through the return jsonify statements. This converts the values to a JSON array which is sent to the template route. The data sent is the user input, and the feedback taken from the JSON file for that lessonid
        if task1 == True:
            if task2 == True:
                print "Task Complete"
                db_answer = answer1 + "\n" + answer2
                lesson = Lesson(db_lessonid, db_lessonname, db_courseid, current_user.username, db_answer, "Task Completed")
                print lesson
                if Lesson.query.filter_by(username=current_user.username, lessonid=db_lessonid).scalar() is None:
                    db.session.add(lesson)
                    db.session.commit()
                if Lesson.query.filter_by(username=current_user.username, lessonid=db_lessonid).scalar() is not None:    
                    print "User Exists"
                    update = Lesson.query.filter_by(username=current_user.username, lessonid = db_lessonid).first()
                    update.excerciseData = answer1 + "\n" + answer2
                    db.session.commit()
                return jsonify(data={'output':(form.source_code.data),'task':(user_feedback), 'second':(user_feedback_Q2)})
            if task2 == False:
                print "Task 1 Complete, Task 2 Not"
                return jsonify(data={'output':(form.source_code.data),'task':(user_feedback), 'second': (user_incorrect_feedbackQ2)})
        else:
            if task2 == True:
                return jsonify(data={'output':(form.source_code.data),'task': (user_incorrect_feedback), 'second':(user_feedback_Q2)})
            else:
                return jsonify(data={'output':(form.source_code.data),'task':(user_incorrect_feedback), 'second':(user_incorrect_feedbackQ2)})
        return jsonify(data={'output':(form.source_code.data)})
    return jsonify(data=form.errors)

@app.route('/dashboard/<username>/')
@login_required
def dashboard(username):
    user = User.query.filter_by(username=username).first()
    if username != current_user.username:
        return redirect(url_for('.dashboard', username=current_user.username))
    return render_template('dashboard.html', user=user, courses=Course.query.filter_by(coursename='HTML:Introduction'))

@app.route('/dashboard/<username>/course/<courseid>/excercise/<lessonid>/')
@login_required
def excerciseTemplate(username, courseid, lessonid):
    if username != current_user.username:
        return redirect(url_for('.dashboard', username=current_user.username))
    #Creating global variables so that this data can be input into the Database for the POST request
    global excercise_courseid
    global excercise_lessonid
    global answer
    global heading
    excercise_courseid = courseid
    excercise_lessonid = lessonid
    form = MyForm()
    #Loading the JSON file which contains the paragraph data and answer data for the Excercise
    with open ('static/lesson/excercise.json') as jsonData:
        paragraph_data = json.load(jsonData)
    username=User.query.filter_by(username=username).first()
    courseid=Course.query.filter_by(courseid=courseid).first()
    lessonData = LessonData.query.filter_by(lessonid=lessonid).first()
    global excercise_lessonname
    excercise_lessonname = lessonData.lessonname
    #IF statement which means if the User has completed the Excercise successfully previously, it will load their correct data
    if  Lesson.query.filter_by(username=current_user.username, lessonid=excercise_lessonid).scalar() is not None:
        print "User has already done this tutorial"
        loadData = Lesson.query.filter_by(username=current_user.username, lessonid=excercise_lessonid).first()
        form.source_code.data = loadData.excerciseData
    else:
        print "User has not done this tutorial"
    for json_answer in paragraph_data:
        if json_answer['lesson_id'] == lessonData.lessonid:
            output = json_answer['answer']
            output_heading = json_answer['heading']
            answer = str(output)
            heading = str(output_heading)
            print answer
    for paragraph in paragraph_data:
        if paragraph['lesson_id'] == lessonData.lessonid:
            return render_template('excercise.html', form=form, username=username, courseid=courseid, lesson=lessonData, paragraphData=paragraph)
    #return render_template('excercise.html', form=form, username=username, courseid=courseid, lesson=LessonData.query.filter_by(lessonid=lessonid, lessontype='Excercise').first())

@app.route('/dashboard/excercise/post/', methods=['POST'])
def excercise():
    form = MyForm()
    if form.validate_on_submit() and request.method == 'POST':
        userInput = form.source_code.data
        excercise_answer = str(answer)
        heading_search = str(heading)
        print heading_search
        soup = BeautifulSoup(userInput)
        excercise = None
        if soup.find(heading_search) is None:
            print "Correct Heading for Answer Not entered"
            excercise = False
            print "Incorrect Answer"
        else:
            print "Correct Heading for the Answer Found"
            if excercise_answer in userInput:
                excercise = True
                print "Correct Answer Found"
            else:
                excercise = False
                print "Incorrect Answer"
        if excercise == True:
            print "Excercise Complete"
            #return jsonify(data={'message':(userInput), 'task':'Correct Answer, Excercise Completed'})
            excercise1 = Lesson(excercise_lessonid, excercise_lessonname, excercise_courseid, current_user.username, excercise_answer, "Excercise Completed")
            if Lesson.query.filter_by(username=current_user.username, lessonid=excercise_lessonid).scalar() is None:
                db.session.add(excercise1)
                db.session.commit()
            return jsonify(data={'message':(userInput), 'task':'Correct Answer, Excercise Completed'})
            if Lesson.query.filter_by(username=current_user.username, lessonid=excercise_lessonid).scalar() is not None:
                print "User has already completed this Excercise!!!"
            #update = Lesson.query.filter_by(username=current_user.username, lessonid = db_lessonid).first()
            #update.excerciseData = excercise_answer
        #db.session.commit()
        else:
            return jsonify(data={'message':(userInput), 'task':'Incorrect Answer'})
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
    if lessonid == lessonid:
        with open ('static/quiz/%s.json' %lessonid) as jsonQuizData:
            quiz_data = json.load(jsonQuizData)
        for quiz_questions in quiz_data:
            quiz_questions = quiz_questions['quiz']
    questions = copy.deepcopy(quiz_questions)
    answerArray = []
    for j in questions:
        answer = questions[j][0]
        answerArray.append(answer)
        #print answerTest
    print answerArray
    for i in questions.keys():
        random.shuffle(questions[i])
    if request.method == "POST":
        correct_questions = 0
        arrayQuestion = []
        wrong_questions = []
        for question in questions.keys():
            answered = request.form[question]
            if answered in answerArray:
                arrayQuestion.append(question)
                correct_questions += 1
            else:
                wrong_questions.append(question)
        flash_correct_question = (", ".join(arrayQuestion))
        flash_wrong_question = (", ".join(wrong_questions))
        print "Wrong Question" + flash_wrong_question
        quiz = Quiz(lessonData.lessonid, courseid.courseid, current_user.username, correct_questions, '')
        if correct_questions == 0:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the "+ lessonData.lessonname +  " quiz, you scored 0 out of 7." + "\n" + "Based on your score we recommend you try all of the lessons in this course, alongside the problem solving excercises. Once you feel confident enough try the quiz again!"
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback #Updates the feedback row with the new Feedback
                db.session.commit()
                flash("You Got 0/7 For the Quiz, You Answered No Questions Correctly.")
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the "+ lessonData.lessonname +  ", you scored 0 out of 7." + "\n" + "Based on your score we recommend you try all of the lessons in this course, alongside the problem solving excercises. Once you feel confident enough try the quiz again!"
                db.session.commit()
                flash("You Got 0/7 For the Quiz, You Answered No Questions Correctly.")
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7" + question + " correctly"
        if correct_questions == 1:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the "+ lessonData.lessonname +  ", you scored 1 out of 7." + "\n" + "Based on your score we recommend you try all of the lessons in this course, alongside the problem solving excercises. Once you feel confident enough try the quiz again!"
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback
                db.session.commit()
                flash("You Got 1/7 For the Quiz, The question you answered correctly was: " +  "\n" + flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the "+ lessonData.lessonname +  ", you scored 1 out of 7." + "\n" + "Based on your score we recommend you try all of the lessons in this course, alongside the problem solving excercises. Once you feel confident enough try the quiz again!"
                db.session.commit()
                print "You scored " +  str(correct_questions) + " out of 7"
                flash("You Got 1/7 For the Quiz, The question you answered correctly was:" +  "\n" + flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
        if correct_questions == 2:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the "+ lessonData.lessonname +  ", you scored 2 out of 7." + "\n" + "Based on your score we recommend you try all of the lessons in this course, alongside the problem solving excercises. Once you feel confident enough try the quiz again!"
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback
                db.session.commit()
                flash("You Got 2/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the "+ lessonData.lessonname +  ", you scored 2 out of 7." + "\n" + "Based on your score we recommend you try all of the lessons in this course, alongside the problem solving excercises. Once you feel confident enough try the quiz again!"
                db.session.commit()
                print "You scored " +  str(correct_questions) + " out of 7"
                flash("You Got 2/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
        if correct_questions == 3:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the " + lessonData.lessonname +", you scored 3 out of 7." + "\n" + "Based on your score we recommend you retry lessons relating to the questions you answered incorrectly. If you cannot remember the questions you answered in correctly." + "\n" + "They were:               " + "\n" + flash_wrong_question
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback
                db.session.commit()
                flash("You Got 3/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the " + lessonData.lessonname +", you scored 3 out of 7." + "\n" + "Based on your score we recommend you retry lessons relating to the questions you answered incorrectly. If you cannot remember the questions you answered in correctly." + "\n" + "They were:               " + "\n" + flash_wrong_question
                db.session.commit()
                print "You scored " +  str(correct_questions) + " out of 7"
                flash("You Got 3/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
        if correct_questions == 4:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the " + lessonData.lessonname +", you scored 4 out of 7." + "\n" + "Based on your score we recommend you retry lessons relating to the questions you answered incorrectly. If you cannot remember the questions you answered in correctly." + "\n" + "They were:               " + "\n" + flash_wrong_question
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback
                db.session.commit()
                flash("You Got 4/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the " + lessonData.lessonname +", you scored 4 out of 7." + "\n" + "Based on your score we recommend you retry lessons relating to the questions you answered incorrectly. If you cannot remember the questions you answered in correctly." + "\n" + "They were:               " + "\n" + flash_wrong_question
                db.session.commit()
                print "You scored " +  str(correct_questions) + " out of 7"
                flash("You Got 4/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
        if correct_questions == 5:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the " + lessonData.lessonname +", you scored 5 out of 7." + "\n" + "Based on your score we recommend you retry lessons relating to the questions you answered incorrectly. If you cannot remember the questions you answered in correctly." + "\n" + "They were:               " + "\n" + flash_wrong_question
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback
                db.session.commit()
                flash("You Got 5/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the " + lessonData.lessonname +", you scored 5 out of 7." + "\n" + "Based on your score we recommend you retry lessons relating to the questions you answered incorrectly. If you cannot remember the questions you answered in correctly." + "\n" + "They were:               " + "\n" + flash_wrong_question
                db.session.commit()
                print "You scored " +  str(correct_questions) + " out of 7"
                flash("You Got 5/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
        if correct_questions == 6:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the " + lessonData.lessonname +", you scored 6 out of 7." + "\n" + "Based on your score we feel that you have gained a good understanding and knowledge for the matieral presented in this course. However remember you can always review amd reflect on the learning matieral in this course!"
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback
                db.session.commit()
                flash("You Got 6/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the " + lessonData.lessonname +", you scored 6 out of 7." + "\n" + "Based on your score we feel that you have gained a good understanding and knowledge for the matieral presented in this course. However remember you can always review and reflect on the learning matieral in this course!"

                db.session.commit()
                print "On the " + lessonData.lessonname +", you scored 6 out of 7." + "\n" + "Based on your score we feel that you have gained a good understanding and knowledge for the matieral presented in this course. However remember you can always review and reflect on the learning matieral in this course!"
                flash("You Got 6/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
        if correct_questions == 7:
            if Quiz.query.filter_by(username=current_user.username, lessonid=lessonData.lessonid).scalar() is None:
                feedback = "On the " + lessonData.lessonname +", you scored 7 out of 7." + "\n" + "Based on your score we feel that you have gained a good understanding and knowledge for the matieral presented in this course. However remember you can always review and reflect on the learning matieral in this course!"
                db.session.add(quiz)
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                update.feedback = feedback
                db.session.commit()
                flash("You Got 7/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
                print "You scored " +  str(correct_questions) + " out of 7"
            else:
                print "User Exists"
                update = Quiz.query.filter_by(username=current_user.username, lessonid = lessonData.lessonid).first()
                print update.quizscore
                update.quizscore = correct_questions
                update.feedback = "On the " + lessonData.lessonname +", you scored 7 out of 7." + "\n" + "Based on your score we feel that you have gained a good understanding and knowledge for the matieral presented in this course. However remember you can always review and reflect on the learning matieral in this course!"
                db.session.commit()
                print "You scored " +  str(correct_questions) + " out of 7"
                flash("You Got 7/7 For the Quiz, The Questions you answered correctly were: "+ flash_correct_question)
                return redirect(url_for('.quizTemplate', lessonid=lessonData.lessonid, courseid=courseid.courseid, username=current_user.username))
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
    quizData = Quiz.query.filter_by(courseid = courseid, username=current_user.username).first()
    taskData = Lesson.query.filter_by(courseid=courseid ,username=current_user.username).first()
    courseid = Course.query.filter_by(courseid = courseid).first()
    return render_template('course.html', username=username, course=courseid, quiz=quizData,task=taskData, lessons=LessonData.query.filter_by(courseid=courseid.courseid, lessontype='Lesson'), excercises=LessonData.query.filter_by(courseid=courseid.courseid, lessontype='Excercise'), quizzes=LessonData.query.filter_by(courseid=courseid.courseid, lessontype='Quiz'))

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

@app.errorhandler(500)
def internal_error(error):
    return "hello"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
