from bokeh.plotting import figure
from h5py import File
import numpy as np
from bokeh.embed import components
import flask_bootstrap
from flask import Flask, render_template, url_for, request, redirect
from flask_login import LoginManager

# Создание основного приложения
app = Flask(__name__)
bootstrap = flask_bootstrap.Bootstrap(app)
login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'


file = File('static/mat/2022-02-04-d3.mat')

light_curve = file['lightcurvesum_global']
unix_time = file['unixtime_global']
last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]

x = np.concatenate(unix_time)
y = np.concatenate(light_curve)


plot = figure(title='Light curve', x_axis_label='Time, 10^5', y_axis_label='Intensity', width=1000)
plot.line(x, y, legend_label='', line_width=2)
script, div = components(plot)


@app.route('/')
def index():
    return render_template('index.html', script=script, div=div)


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

