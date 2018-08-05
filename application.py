from flask import Flask, render_template, request
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKey'

class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class RegisterForm(Form):
    firstname = StringField('First Name', validators=[InputRequired()])
    lastname = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(message='Error')])    
    password = PasswordField('Password', validators=[InputRequired()])
    reenterpassword = PasswordField('Re-Enter Password', validators=[InputRequired()])

@app.route("/")
def route():
    return render_template('main.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        return "Form Successfully Submitted"
    return render_template('login.html', form=form)


@app.route("/register/", methods=['GET','POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        return "hello"
    return render_template('register.html', form=form)

@app.errorhandler(404)
def error_page(error):
    return "Couldn't find the page"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
