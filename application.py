from flask import Flask, render_template, request, flash, session, redirect, abort, url_for
from flask_wtf import Form
from flask_login import LoginManager
from flask_login import current_user, login_user, login_required, UserMixin, logout_user
from wtforms import StringField, PasswordField, validators
from wtforms.validators import InputRequired, Email
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kevin/HonoursProject/database.db'
app.config['SECRET_KEY'] = 'SecretKey'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
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
    firstname = StringField('Please enter your First Name', validators=[InputRequired()])
    lastname = StringField('Please Enter your Last Name', validators=[InputRequired()])
    username = StringField('Please enter your Username', validators=[InputRequired()])
    email = StringField('Please enter your Email', validators=[InputRequired(), Email(message='Error')])    
    password = PasswordField('Please enter your Password', validators=[InputRequired(), validators.EqualTo('confirm', message='Passwords MUst Match')])
    confirm = PasswordField('Please re-enter your Password', validators=[InputRequired()])

@app.route("/")
def main():
    return render_template('main.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return "Already logged in"
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
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        if User.query.filter_by(email=form.email.data).first():
            return 'Email already exists'
        elif User.query.filter_by(username=form.username.data).first():
            return 'Username already exists'
        else:
            user = User(form.firstname.data, form.lastname.data, form.email.data, form.username.data, (form.password.data))       
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

@app.route('/dashboard/template/')
def template():
    return render_template('template.html')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('.main'))


@app.errorhandler(404)
def error_page(error):
    return "Couldn't find the page"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
