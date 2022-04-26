# Инициализируем все необходимые библиотеки

import base64
import mimetypes
import os
import smtplib
import string
from random import random
import random

import time
from datetime import datetime
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hashlib import md5
from threading import Thread

from dotenv import load_dotenv
import numpy as np
import plotly
import plotly.express as px
import requests
from flask import *
from flask import Flask, render_template, redirect
from flask import request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from h5py import File
from scipy import signal
from waitress import serve

from data import db_session
from data.structure import User, Comments, Email_services
from forms.forgot_password import ResetPasswordRequestForm
from forms.login import LoginForm
from forms.new_user import RegisterForm
from forms.profile_redact import UpdateAccountForm
from forms.reset_password_form import ResetPasswordForm
import pandas as pd
from human_readable_file_size import human_readable_file_size
server = False
load_dotenv()
SMTP_HOST: str = os.environ["HOST"]
SMTP_PORT: int = int(os.environ["PORT"])

# Main app definition

# Инициализируем Flask сервер
app = Flask(__name__, template_folder='templates')
app.config.from_pyfile('config.py')
# Additions:

# Инициализируем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'


def create_mail_server():
    global server
    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
    addr_from = os.getenv("FROM")
    password = os.getenv("PASSWORD")
    server.connect(SMTP_HOST, SMTP_PORT)
    server.login(addr_from, password)


db_session.global_init("db/users.db")  # Подключаем базу данных


def send_async_email(app, msg):
    with app.app_context():
        server.send_message(msg)


def send_email(recipients, subject, plain_text=None, html_text=None, attachments=None):
    if not server:
        create_mail_server()
    addr_from = os.getenv("FROM")
    for email in recipients:
        msg = MIMEMultipart()
        msg['From'] = addr_from
        msg['To'] = email
        msg['Subject'] = subject
        if html_text:
            msg.attach(MIMEText(html_text, 'html'))
        if plain_text:
            msg.attach(MIMEText(plain_text, 'plain'))
        if attachments:
            process_attachments(msg, attachments)
        try:
            Thread(target=send_async_email, args=(app, msg)).start()
        except:
            return "Some error happened!!"


def attach_file(msg, f):
    attach_types = {
        'text': MIMEText,
        'image': MIMEImage,
        'audio': MIMEAudio,
    }
    filename = os.path.basename(f)
    ctype, encoding = mimetypes.guess_type(f)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    with open(f, mode='rb' if maintype != 'text' else 'r') as fp:
        if maintype in attach_types:
            file = attach_types[maintype](fp.read(), _subtype=subtype)
        else:
            file = MIMEBase(maintype, subtype)
            file.set_payload(fp.read())
            encoders.encode_base64(file)
        file.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(file)


def process_attachments(msg, attachments):
    for f in attachments:
        if os.path.isfile(f):
            attach_file(msg, f)
        elif os.path.exists(f):
            dir = os.listdir(f)
            for file in dir:
                attach_file(msg, f + '/' + file)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email([user.email], '[PGI] Reset Your Password',
               html_text=render_template('email/reset_password.html',
                                         user=user, token=token))


def Heatmap(frame: int, max_min_values: list):  # Функция построения графика heatmap

    """
    :param frame: номер текущего фрейма
    :param max_min_values: минимальное и максимальное значение scale. задаётся пользователем. в случае выбора autoscale оба значения нули
    :return: json строка, в которой лежит генератор построения Heatmap
    """

    array = data_hm[frame]  # Достаём из текущего файла данные для построения

    # Построим генератор графика
    fig = px.imshow(array,
                    zmax=max(max_min_values),  # Все значения больше zmax будут приравняны к zmax при построении
                    zmin=min(max_min_values),  # Все значения меньше zmin будут приравняны к zmix при построении
                    aspect='equal',  # для того, чтобы каждое значение было квадратным
                    origin='upper'
                    )
    # Если zmax = zmin, график строится по autoscale

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def Keogram(max_min_values: list):  # Функция построения графика keogram

    """
    :param max_min_values: минимальное и максимальное значение scale. задаётся пользователем. в случае выбора autoscale оба значения нули
    :return: json строка, в которой лежит генератор построения Keogram
    """


    diag_global = file["diag_global"]  # Достаём из текущего файла данные для построения
    diag_global = np.rot90(diag_global)  # Преобразуем данные в необходимый формат

    # Сожмём данные из diag global
    diag_global_2 = signal.decimate(diag_global,
                                    q=q,  # выход будет в q раз меньше
                                    ftype='fir'  # Используется функция фильтра с конечной импульсной характеристикой
                                    )


    # Построим генератор графика
    fig = px.imshow(diag_global_2,
                    # Множество значений по оси Y. значение задано массивом из 16 чисел:
                    # диагонали heatmap в этом моменте времени
                    x=UNIX_TIME_2,
                    # Множество значений по оси X. Каждое Задано датой и временем текущей точки
                    zmax=max(max_min_values),  # Все значения больше zmax будут приравняны к zmax при построении
                    zmin=min(max_min_values),  # Все значения меньше zmin будут приравняны к zmix при построении
                    aspect='auto'  # Каждое значение по размеру насраивается автоматически от масштаба графика
                    )

    # Настроим, что будет выводиться при наведение курсора на точку графика
    fig.update_traces(hovertemplate='<i>Value</i>: %{y:.2f}' +
                                    '<br><b>Time</b>: %{x|%H:%M:%S}<br>',  # отображается значение по y и время по x
                      showlegend=False  # Не показывать легенду
                      )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def Light_curve():  # Функция построения графика Light curve

    """
    :return: json строка, в которой лежит генератор построения Keogram
    """


    light_curve = file['lightcurvesum_global']  # Достаём из текущего файла данные для построения

    light_curve = np.ravel(light_curve)  # приведём данные к нужному формату

    light_curve_2 = signal.decimate(light_curve,
                                    q=q,  # выход будет в q раз меньш
                                    ftype='fir',  # Используется функция фильтра с конечной импульсной характеристикой
                                    n=8  # Порядок фильтра
                                    )

    fig = px.line(x=UNIX_TIME_2,  # Множество значений по оси X. Каждое Задано датой и временем текущей точки
                  y=light_curve_2  # Множество значений по оси Y. Каждое Задано интенсивностью света в данной точке
                  )

    # Настроим, что будет выводиться при наведение курсора на точку графика
    fig.update_traces(mode="markers+lines",

                      hovertemplate='<i>Value</i>: %{y:.2f}' +  # отображается интенсивность по y и время по x
                                    '<br><b>Time</b>: %{x|%H:%M:%S}<br>',

                      showlegend=False)

    # Настроим
    fig.update_layout(legend_orientation="h",  #
                      legend=dict(x=.5, xanchor="center"),
                      xaxis_title="Time", yaxis_title="Intensity",
                      )
    return fig


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    user_id = User.verify_reset_password_token(token)
    curr_user = db_sess.query(User).filter(User.id == user_id).first()
    if not curr_user:
        return redirect(url_for('main'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        curr_user.set_password(form.password.data)
        db_sess.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=["GET", "POST"])
def main():
    global file, UNIX_TIME, UNIX_TIME_2, q, data_hm, max_hm
    # db_sess = db_session.create_session()
    # here we can use
    # if current_user.is_authenticated:
    if request.method == 'POST':
        if request.values.get('type') == 'first_event':
            heatmap_graph = Heatmap(1, [20000, 200000])
            keogram_graph = Keogram([20000, 200000])
            fig3 = Light_curve()

            lightcurve_graph = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            result = {'heatmap': heatmap_graph, 'keogram': keogram_graph, 'lightcurve': lightcurve_graph}
            return result

        elif request.values.get('type') == 'keogram_slider_event':
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            graphJSON = Keogram(values)
            return graphJSON
        elif request.values.get('type') in ['heatmap_slider_event', 'heatmap_button_event', 'lightcurve_click_event']:
            current = 0
            if request.values.get('type') in ['heatmap_button_event', 'heatmap_slider_event']:
                current = int(request.values.get('current'))
                if request.values.get('type') == 'heatmap_button_event':
                    changes = {'play': 2, 'next': 1, 'next2': 10, 'next3': 1000, 'last': -1, 'last2': -10,
                               'last3': -1000}
                    if 0 <= current + changes[request.values.get('pos')] < max_hm:
                        current += changes[request.values.get('pos')]
                    elif current + changes[request.values.get('pos')] < 0:
                        current = 0
                    elif current + changes[request.values.get('pos')] >= max_hm:
                        current = max_hm - 1
            else:
                x = 'T'.join(request.values.get('x').split()) + '.000000000'
                current = np.where(UNIX_TIME_2.astype(np.str_) == x)[0][0] * q
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            if request.values.get('is_auto') == 'true':
                values = [0, 0]
            graphJSON = Heatmap(current, values)

            current_time = UNIX_TIME[int(current)]
            current_time = time.strftime("%H:%M:%S", time.localtime(int(current_time)))
            result = {'heatmap': graphJSON, 'current': int(current),
                      'title': f"This is frame number {int(current) + 1} out of {len(data_hm)} <br>"
                               f" time: {current_time}", }
            return result

        elif request.values.get('type') == 'date_event':
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                      'Nov', 'Dec']
            date = request.values.get('date').split()

            def to_date(date):
                return '0' * (2 - len(str(date))) + str(date)

            filename = f'{date[-1]}-{to_date(months.index(date[1]) + 1)}-{to_date(date[2])}-d3.mat'
            print(filename)

            file = File(f'./static/mat/{filename}')

            unix_time = file['unixtime_global']

            last = np.add(unix_time[-1], 5)
            unix_time = np.append(unix_time, last)
            unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
            UNIX_TIME = np.ravel(unix_time)

            q = 6200  # То, во сколько раз вы прорежаете массив (берете каждый q-й элемент)
            a = np.zeros(q - UNIX_TIME.shape[0] + ((UNIX_TIME.shape[0] + 1) // q) * q)
            UNIX_TIME_2 = np.concatenate((UNIX_TIME, a)).reshape(-1, q)[:, 0]
            UNIX_TIME_2 = pd.to_datetime(pd.Series(UNIX_TIME_2 // 1), unit='s').to_numpy()
            data_hm = file['pdm_2d_rot_global']
            max_hm = len(data_hm)
            return ''

        elif request.values.get('type') == 'get_date_list':

            date_list = []

            for elem in os.listdir('./static/mat'):
                elem = elem.split('-')
                tpl = (elem[2], elem[1], elem[0])
                date_list.append(tpl)

            return {'data': tuple(date_list)}


    else:
        return render_template('main.html', he=current_user, load=True,
                               we_are_home=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        nick_ok_letters = ["_", ".", "-"] + [str(n) for n in range(10)] + \
                          [chr(_) for _ in range(ord("A"), ord("Z") + 1)] + [chr(_) for _ in
                                                                             range(ord("a"), ord("z") + 1)]
        for letter in form.nickname.data:
            if letter not in nick_ok_letters:
                return render_template('register.html', title='Регистрация',
                                       form=form, message="Имя пользователя содержит недопустимые символы")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(form.nickname.data == User.nickname).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такое имя пользователя уже существует")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Учетная запись с таким почтовым адресом уже сущестует")

        print("-" * 50, "New user is created", "-" * 50, sep="\n")
        profile_img = requests.get('http://www.gravatar.com/avatar/' + md5(
            form.email.data.encode()).hexdigest() + '?d=identicon&s=200').content
        user = User(
            nickname=form.nickname.data.lower(),
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            profile_photo=profile_img,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        info = user.info()
        admins = db_sess.query(User).filter(User.is_admin).all()
        admin_mails = [_.email for _ in admins]

        send_email(admin_mails, '[PGI] New user',
                   plain_text=f'Зарегистрировался новый пользователь со следующими данными: {info}')

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.nick.data.lower()).first()
        if not user:
            user = db_sess.query(User).filter(User.nickname == form.nick.data.lower()).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_seen = datetime.utcnow()
            db_sess.add(user)
            db_sess.commit()
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        curr_user = db_sess.query(User).filter_by(email=form.nick.data.lower()).first()
        if not curr_user:
            curr_user = db_sess.query(User).filter_by(nickname=form.nick.data.lower()).first()
        if curr_user:
            print(curr_user.name, curr_user.surname, "requested reset password")
            send_password_reset_email(curr_user)
        else:
            return render_template('reset_password_request.html',
                                   title='Reset Password', form=form,
                                   message="Пользователь не существует")
        # flash('Check your email for the instructions to reset your password')
        return redirect(f'/forgot_password/ok/{curr_user.nickname}')
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/forgot_password/ok/<nickname>')
def okay(nickname):
    db_sess = db_session.create_session()
    curr_user = db_sess.query(User).filter(User.nickname == nickname.lower()).first()
    email = curr_user.email.lower()
    domain = email.split("@")[1]
    service = db_sess.query(Email_services).filter(Email_services.domain == domain).first()
    return render_template('we_sent_email.html', service=service)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def abort_if_not_found(error):
    return render_template('404.html')


def save_picture(form_picture, user_nickname):
    random_hex = "".join(random.sample(string.ascii_letters + string.digits, 10))
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == user_nickname).first()



@app.route('/users/<nickname>', methods=['GET', 'POST'])
def user(nickname):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == nickname.lower()).first()
    form = UpdateAccountForm()
    if request.method == 'GET':
        if not current_user.is_authenticated:
            abort(404)
        if not user:
            flash('User ' + nickname + ' not found.', 'warning')
            return redirect("/")
        profile_pic = (base64.b64encode(user.profile_photo)).decode("utf-8")
        return render_template('user/user.html', user=user, he=current_user,
                               profile_pic=profile_pic, form=form)
    else:
        if form.validate_on_submit():
            if form.picture.data:
                pass
            same_nicks_exist = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
            if same_nicks_exist:
                if same_nicks_exist.nickname != current_user.nickname:
                    profile_pic = (base64.b64encode(user.profile_photo)).decode("utf-8")
                    return render_template('user/user.html', user=user,
                                           profile_pic=profile_pic, form=form, he=current_user,
                                           error_msg=['That username is taken. Please choose a different one.'])
                else:
                    user.nickname = form.nickname.data
            else:
                user.nickname = form.nickname.data

            this_email_exists = db_sess.query(User).filter(User.email == form.email.data).first()
            if this_email_exists:
                if this_email_exists.email != current_user.email:
                    profile_pic = (base64.b64encode(user.profile_photo)).decode("utf-8")
                    return render_template('user/user.html', user=user,
                                           profile_pic=profile_pic, form=form, he=current_user,
                                           error_msg=['That email is taken. Please choose a different one.'])
                else:
                    user.email = form.email.data
            else:
                user.email = form.email.data
            user.name = form.name.data
            user.surname = form.surname.data
            db_sess.add(user)
            db_sess.commit()
            flash('Your account has been updated!', 'success')
            return redirect(f'/users/{form.nickname.data}')
        else:
            pass


@app.route('/all_data_files')
def all_data_files():
    files_list = []
    for filename in os.listdir('static/mat/'):
        if not filename.startswith('.'):
            abs_path = os.path.abspath(os.path.join('static/mat/', filename))
            print("Abs path is", abs_path)
            bytes_size = os.path.getsize(abs_path)
            norm_syze: str = human_readable_file_size(bytes_size)
            files_list.append((filename, norm_syze, abs_path))
    files_list.sort(key=lambda _: _[0])
    return render_template('all_data_files.html', files_list=files_list, count=1, he=current_user)


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
    # serve(app, host='0.0.0.0', port=5000)
    if server:
        server.quit()
