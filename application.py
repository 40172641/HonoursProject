from flask import Flask, render_template, abort, request
app = Flask(__name__)

@app.route("/")
def route():
    return render_template('main.html')

@app.route("/login/", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
    return render_template('login.html')

@app.route("/register/", methods=['GET','POST'])
def register():
    error = None
    if request.method == 'POST':
        registerUsername = request.form['username']
        registerPassword = request.form['password']
    return render_template('register.html')

@app.errorhandler(404)
def error_page(error):
    return "Couldn't find the page"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
