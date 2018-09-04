from flask import Flask, render_template, request, flash, session, redirect, abort, url_for, jsonify, make_response
import json
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

class MyForm(Form):
    source_code = CodeMirrorField(language='python', config={'lineNumbers' : 'true'})
    body = StringField('Text', widget=TextArea(), default='Please add content')
    text = TinyMceField('My WTF TinyMCEField',tinymce_options={'readonly':'1', 'height':'531', 'width':'393', 'valid_elements':'*[*]', 'allow_script_urls': 'true', 'extended_valid_elements': 'script[language|src=https://cloud.tinymce.com/stable/tinymce.min.js]'})

@app.route("/")
def index ():
    form = MyForm()
    return render_template('excercise1.html', form=form)

@app.route('/d/', methods=['POST'])
def excercise():
    form = MyForm()
    if form.validate_on_submit() and request.method == 'POST':
        userInput = form.source_code.data
        form.text.data = userInput
        return jsonify(data={'message': (form.text.data)})
    return jsonify(data=form.errors)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
