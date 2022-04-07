import plotly
from flask import *
import plotly.express as px
import numpy as np
from h5py import File
from scipy import signal
import os
from flask import Flask, render_template, redirect, make_response
from flask import request, session, jsonify
from data import db_session
from data.structure import User, Comments
from forms.new_user import RegisterForm
from forms.login import LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import reqparse, abort, Api, Resource


file = File('./static/mat/2022-01-26-d3-nz.mat')

unix_time = file['unixtime_global']

last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)


def Heatmap(frame: int, max_min_values: list):
    data = file['pdm_2d_rot_global']
    array = data[frame]
    print(max_min_values)
    fig = px.imshow(array, zmax=max(max_min_values), zmin=min(max_min_values), aspect='equal', origin='upper')

    fig.update_layout(legend_orientation="h",
                      legend=dict(
                          title=f"This is frame number {frame} out of {len(data)} <br> timestamp is {UNIX_TIME[frame]:.3f} seconds",
                          x=.5, xanchor='center', bordercolor='red', borderwidth=3, ),
                      showlegend=True,
                      xaxis_title="",
                      yaxis_title="",
                      )

    return fig


def Keogram(max_min_values: list):
    diag_global = file["diag_global"]
    diag_global = np.rot90(diag_global)
    print("Size of diag_global:", len(diag_global), len(diag_global[0]), "\nsize of UNIX_TIME:", len(UNIX_TIME), 1)

    q = 321  # То, во сколько раз вы прорежаете массив (берете каждый q-й элемент)
    a = np.zeros(q - UNIX_TIME.shape[0] + ((UNIX_TIME.shape[0] + 1) // q) * q)
    UNIX_TIME_2 = np.concatenate((UNIX_TIME, a)).reshape(-1, q)[:, 0]
    diag_global_2 = signal.decimate(diag_global, q=q, ftype='fir')

    fig = px.imshow(diag_global_2, x=UNIX_TIME_2, zmax=max(max_min_values), zmin=min(max_min_values), aspect='auto')

    fig.update_layout()
    return fig


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = '820b4ad02742e6630b554a48de7d2d9f'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

api = Api(app)

db_session.global_init("db/users.db")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=["GET", "POST"])
def main():
    # db_sess = db_session.create_session()
    # here we can use
    # if current_user.is_authenticated:
    if request.method == 'POST':
        if request.values.get('type') == 'first_event':
            fig1 = Heatmap(1, [20000, 200000])
            fig2 = Keogram([20000, 200000])
            heatmap_graph = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            keogram_graph = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            result = {'heatmap': heatmap_graph, 'keogram': keogram_graph}
            return result
        elif request.values.get('type') == 'heatmap_button_event':
            current = int(request.values.get('current'))
            changes = {'next': 1, 'next2': 10, 'next3': 1000, 'last': -1, 'last2': -10, 'last3': -1000}
            current += changes[request.values.get('pos')]
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            fig = Heatmap(current, values)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON
        elif request.values.get('type') == 'heatmap_slider_event':
            current = int(request.values.get('current'))
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            fig = Heatmap(current, values)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON
        elif request.values.get('type') == 'keogram_slider_event':
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            fig = Keogram(values)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON

    else:
        files_list = []
        for elem in os.listdir('static/mat/'):
            if not elem.startswith('.'):
                files_list.append(elem)
        return render_template('main.html', files_list=files_list)



@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def abort_if_not_found(error):
    return render_template('404.html')


if __name__ == "__main__":
    app.run(port=8405, debug=True)
