from flask import Flask, render_template, url_for, request, redirect
from flask_login import LoginManager

# Создание основного приложения
app = Flask(__name__)
login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'


@app.route('/')
def index():
    return render_template('templates/index.html')


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)



if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')

