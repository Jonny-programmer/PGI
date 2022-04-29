# -*- encoding: utf-8 -*-
# Инициализируем все необходимые библиотеки
import base64
import io
import mimetypes
import os
import smtplib
import uuid as uuid
import time

from PIL import Image
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
from werkzeug.utils import secure_filename
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

# Настраиваем SMTP_SERVER

server = False
load_dotenv()
SMTP_HOST: str = os.environ["HOST"]
SMTP_PORT: int = int(os.environ["PORT"])

# Main app definition
filename = None
# Инициализируем Flask сервер
app = Flask(__name__, template_folder='templates')
app.config.from_pyfile('config.py')
# Additions:

# Инициализируем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

db_session.global_init("db/users.db")  # Подключаем базу данных


def create_mail_server():
    global server
    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
    addr_from = os.getenv("FROM")
    password = os.getenv("PASSWORD")
    server.connect(SMTP_HOST, SMTP_PORT)
    server.login(addr_from, password)


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
    """Функция прикрепляет файл к письму"""
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
    """Функция обрабатывает прикрепление множества файлов"""
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


def Keogram(max_min_values: list):  # Функция построения графика keogramm
    """
    :param max_min_values: минимальное и максимальное значение scale. задаётся пользователем. в случае выбора autoscale оба значения нули
    :return: json строка, в которой лежит генератор построения Keogram
    """
    q = 6200
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


def Light_curve(UNIX_TIME_2, x_range=None, y_range=None, cord1=0, cord2=-1):  # Функция построения графика Light curve
    """
    :param UNIX_TIME_2: параметры времени по оси x
    :param x_range: по умолчанию none. если переданы x0 и x1 ставит область просмотра графика от x0 до x1
    :param y_range: по умолчанию none. если переданы y0 и y1 ставит область просмотра графика от y0 до y1
    :param cord1: По умолчанию 0. Строиться график будет начиная с индекса cord1 в файле
    :param cord2: По умолчанию -1. Строиться график будет до индекса cord2 в файле
    :return: json строка, в которой лежит генератор построения Light curve
    """

    light_curve = file['lightcurvesum_global'][cord1: cord2]  # Достаём из текущего файла данные для построения

    print(f'light_curve: {light_curve.shape}')
    print(f'q: {q}')
    light_curve = np.ravel(light_curve)  # приведём данные к нужному формату
    light_curve_2 = signal.decimate(light_curve,
                                    q=q,  # выход будет в q раз меньше
                                    ftype='fir',  # Используется функция фильтра с конечной импульсной характеристикой
                                    n=8  # Порядок фильтра
                                    )
    print(f'light_curve_2: {light_curve_2.shape}')
    fig = px.line(x=UNIX_TIME_2,  # Множество значений по оси X. Каждое Задано датой и временем текущей точки
                  y=light_curve_2,  # Множество значений по оси Y. Каждое Задано интенсивностью света в данной точке
                  range_x=x_range,
                  range_y=y_range
                  )

    # Настроим, что будет выводиться при наведении курсора на точку графика
    fig.update_traces(mode="markers+lines",
                      hovertemplate='<i>Value</i>: %{y:.2f}' +  # отображается интенсивность по y и время по x
                                    '<br><b>Time</b>: %{x|%H:%M:%S}<br>',
                      showlegend=False)

    # Настроим
    fig.update_layout(legend_orientation="h",  #
                      legend=dict(x=.5, xanchor="center"),
                      xaxis_title="Time", yaxis_title="Intensity",
                      hovermode="x unified",
                      )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        # Пользователь уже вошел в аккаунт, ему не надо сбрасывать пароль
        return redirect(url_for('main'))
    # Узнаем, какой пользователь пришел по этой ссылке
    user_id = User.verify_reset_password_token(token)
    curr_user = db_sess.query(User).filter(User.id == user_id).first()
    if not curr_user:
        # Если пользователя, для которого была сгенерирована ссылка, нет
        return redirect(url_for('main'))
    form = ResetPasswordForm()
    # Форма для сброса пароля
    if form.validate_on_submit():
        # Устанавливаем новый пароль
        curr_user.set_password(form.password.data)
        db_sess.commit()
        flash('Your password has been reset.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=["GET", "POST"])
def main():
    global file, UNIX_TIME, UNIX_TIME_2, q, data_hm, max_hm, UNIX_TIME_for_lightcurve, UNIX_TIME_2_for_lightcurve, filename
    # db_sess = db_session.create_session()
    # here we can use
    # if current_user.is_authenticated:
    if request.method == 'POST':
        if request.values.get('type') == 'first_event':
            heatmap_graph = Heatmap(1, [20000, 200000])
            keogram_graph = Keogram([20000, 200000])

            lightcurve_graph = Light_curve(UNIX_TIME_2)
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
                x = request.values.get('x')
                print(f'x: {x}')
                if len(x.split('.')) > 1:
                    x = int(time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))) + 3 * 60 * 60
                else:
                    x = int(time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S'))) + 3 * 60 * 60
                print(x)

                def find_nearest(array, value):
                    array = np.asarray(array)
                    idx = (np.abs(array - value)).argmin()
                    return idx

                current = find_nearest(UNIX_TIME, x)

                print(current)

                # current = np.where(UNIX_TIME_2.astype(np.str_) == x)[0][0] * q
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            if request.values.get('is_auto') == 'true':
                values = [0, 0]
            graphJSON = Heatmap(current, values)

            current_time = UNIX_TIME[int(current)]
            f = str(current_time).split('.')[1][:4]
            current_time = time.strftime("%H:%M:%S", time.localtime(int(current_time) - 3 * 60 * 60))
            result = {'heatmap': graphJSON, 'current': int(current),
                      'title': f" time: {current_time}.{f}", }
            return result
        elif request.values.get('type') == 'date_event':
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                      'Nov', 'Dec']
            date = request.values.get('date').split()

            def to_date(date):
                return '0' * (2 - len(str(date))) + str(date)

            filename = f'{date[-1]}-{to_date(months.index(date[1]) + 1)}-{to_date(date[2])}-d3.mat'

            file = File(f'./static/mat/{filename}')

            unix_time = file['unixtime_global']

            last = np.add(unix_time[-1], 5)
            unix_time = np.append(unix_time, last)
            unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
            UNIX_TIME = np.ravel(unix_time)

            UNIX_TIME_for_lightcurve = UNIX_TIME.copy()

            q = 6200  # То, во сколько раз вы прорежаете массив (берете каждый q-й элемент)
            a = np.zeros(q - UNIX_TIME.shape[0] % q if UNIX_TIME.shape[0] % q else 0)
            UNIX_TIME_2 = np.concatenate((UNIX_TIME, a)).reshape(-1, q)[:, 0]
            UNIX_TIME_2 = pd.to_datetime(pd.Series(UNIX_TIME_2), unit='s').to_numpy()

            UNIX_TIME_2_for_lightcurve = UNIX_TIME_2.copy()

            data_hm = file['pdm_2d_rot_global']
            max_hm = len(data_hm)
            return ''
        elif request.values.get('type') == 'get_date_list':
            date_list = []

            for elem in os.listdir('./static/mat'):
                if not elem.endswith('.mat') or elem.startswith("."):
                    continue
                elem = elem.split('-')
                tpl = (elem[2], elem[1], elem[0])
                date_list.append(tpl)

            return {'data': tuple(date_list)}
        elif request.values.get('type') == 'lightcurve_change':
            x0 = 'T'.join(request.values.get('x0').split())
            x1 = 'T'.join(request.values.get('x1').split())
            y0 = float(request.values.get('y0'))
            y1 = float(request.values.get('y1'))

            if not (x0 and x1 and y0 and x1):
                return ''

            print(x0, x1, y0, y1)
            x_range = [x0, x1]
            y_range = [y0, y1]

            def find_nearest(array, value):
                array = np.asarray(array)
                idx = (np.abs(array - value)).argmin()
                return idx

            x0 = np.array([x0]).astype(np.datetime64)
            x1 = np.array([x1]).astype(np.datetime64)

            current_x_0 = find_nearest(UNIX_TIME_2_for_lightcurve, x0) * q
            current_x_1 = find_nearest(UNIX_TIME_2_for_lightcurve, x1) * q

            if not len(UNIX_TIME_for_lightcurve[current_x_0: current_x_1]):
                return ''

            UNIX_TIME_for_lightcurve = UNIX_TIME_for_lightcurve[current_x_0: current_x_1]

            q = len(UNIX_TIME_for_lightcurve) // 150

            a = np.zeros(q - UNIX_TIME_for_lightcurve.shape[0] % q if UNIX_TIME_for_lightcurve.shape[0] % q else 0)
            UNIX_TIME_2_for_lightcurve = np.concatenate((UNIX_TIME_for_lightcurve, a))
            UNIX_TIME_2_for_lightcurve = UNIX_TIME_2_for_lightcurve.reshape(-1, q)[:, 0]
            UNIX_TIME_2_for_lightcurve = pd.to_datetime(pd.Series(UNIX_TIME_2_for_lightcurve), unit='s').to_numpy()

            lightcurve_graph = Light_curve(UNIX_TIME_2_for_lightcurve, x_range=x_range, y_range=y_range,
                                           cord1=current_x_0,
                                           cord2=current_x_1)

            return {'lightcurve': lightcurve_graph}
        elif request.values.get('type') == 'lightcurve_all_graph_event':
            q = 6200

            UNIX_TIME_2_for_lightcurve = UNIX_TIME_2.copy()
            UNIX_TIME_for_lightcurve = UNIX_TIME.copy()
            lightcurve_graph = Light_curve(UNIX_TIME_2)
            return {'lightcurve': lightcurve_graph}

        elif request.values.get('type') == 'wavelet_event':
            wavelet = file['cwt_global']
            local_q = 10000
            print(wavelet.shape)
            a = np.zeros(local_q - UNIX_TIME.shape[0] % local_q if UNIX_TIME.shape[0] % local_q else 0)
            local_UNIX_TIME_2 = np.concatenate((UNIX_TIME, a)).reshape(-1, local_q)[:, 0]
            local_UNIX_TIME_2 = pd.to_datetime(pd.Series(local_UNIX_TIME_2), unit='s').to_numpy()

            wavelet_2 = signal.decimate(wavelet,
                                        q=local_q,  # выход будет в q раз меньше
                                        ftype='fir',
                                        n=5
                                        # Используется функция фильтра с конечной импульсной характеристикой
                                        )
            fig = px.imshow(wavelet_2, x=local_UNIX_TIME_2)
            fig.show()
            return ''



        else:
            db_sess = db_session.create_session()
            timestamp = request.values.get('timestamp')
            # 2022-02-03 17:46:12
            comment = request.values.get('comment')
            is_private = request.values.get('is_private')
            if not timestamp:
                return render_template('main.html', he=current_user, load=False, we_are_home=True,
                                       message='Time field is empty. To fill it, tap to lightcurve')
            if not comment:
                return render_template('main.html', he=current_user, load=False, we_are_home=True,
                                       message='Please enter a comment')
            if is_private:
                is_private = True
            structed_time = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            real_timestamp = datetime.fromtimestamp(time.mktime(structed_time))
            comment = Comments(
                user_id=current_user.id,
                date_created=datetime.now(),
                time_related=real_timestamp,
                mat_file=filename,
                content=comment,
                is_private=is_private,
            )
            db_sess.add(comment)
            db_sess.commit()
            db_sess = db_session.create_session()
            comments = db_sess.query(Comments).filter_by(mat_file=filename).all()
            print(comments)
            for comment in comments:
                print(f"---> {comment.mat_file}")
            print(f"filename is {filename}")
            return render_template('main.html', he=current_user, load=True, we_are_home=True, comments=comments)
    db_sess = db_session.create_session()
    comments = db_sess.query(Comments).filter_by(mat_file=filename).all()
    print(comments)
    return render_template('main.html', he=current_user, load=True, we_are_home=True, comments=comments)


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
            form.email.data.encode()).hexdigest() + '?d=identicon&s=125').content
        new_user = User(
            nickname=form.nickname.data.lower(),
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            profile_pic=save_picture(profile_img, from_gravatar=True),
        )
        new_user.set_password(form.password.data)
        db_sess.add(new_user)
        db_sess.commit()

        # info = user.info()
        # admins = db_sess.query(User).filter(User.is_admin).all()
        # admin_mails = [_.email for _ in admins]

        return redirect('/login')

        # send_email(admin_mails, '[PGI] New user',
        #           plain_text=f'Зарегистрировался новый пользователь со следующими данными: {info}')
        # return redirect('/login')
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
    print(error)
    return render_template('404.html')


@app.errorhandler(500)
def show_error(error):
    print(error)
    return render_template('500.html')


def save_picture(user_form_picture, from_gravatar=None, previous_picture=None):
    if previous_picture:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], previous_picture))
        except FileNotFoundError:
            print("NOT ACHIEVED IN DELETING PREVIOUS IMAGE!!!!")
    output_size = (125, 125)
    if from_gravatar:
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + "default_avatar.png"
        pic_full_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
        i = Image.open(io.BytesIO(user_form_picture))
    else:
        pic_filename = secure_filename(user_form_picture.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename.replace(" ", "_")
        # Save that image
        pic_full_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
        i = Image.open(user_form_picture)
    # Сжимаем изображение до определенного размера
    i.thumbnail(output_size)
    i.save(pic_full_path)
    return pic_name


@app.route('/users/<nickname>', methods=['GET', 'POST'])
def user(nickname):
    db_sess = db_session.create_session()
    user_profile = db_sess.query(User).filter_by(nickname=nickname.lower()).first()
    form = UpdateAccountForm()
    if request.method == 'GET':
        if not current_user.is_authenticated or nickname.lower() != current_user.nickname.lower():
            abort(404)
        if not user_profile:
            flash('User ' + nickname + ' not found.', 'warning')
            return redirect("/")
        return render_template('user/user.html', user=user_profile, he=current_user,
                               form=form, title='Redact profile')

    if form.validate_on_submit():
        if form.picture.data:
            # Saving new image name to db
            new_image_path = save_picture(form.picture.data, previous_picture=user_profile.profile_pic)
            user_profile.profile_pic = new_image_path
            db_sess.add(user_profile)
            db_sess.commit()
            print("=" * 50, "Success!!", "*" * 50, sep="\n")
        same_nicks_exist = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if same_nicks_exist:
            if same_nicks_exist.nickname != current_user.nickname:
                return render_template('user/user.html', user=user_profile,
                                       form=form, he=current_user,
                                       error_msg=['That username is taken. Please choose a different one.'],
                                       title='Redact profile')
            else:
                user_profile.nickname = form.nickname.data
        else:
            nick_ok_letters = ["_", ".", "-"] + [str(n) for n in range(10)] + \
                              [chr(_) for _ in range(ord("A"), ord("Z") + 1)] + [chr(_) for _ in
                                                                                 range(ord("a"), ord("z") + 1)]
            for letter in form.nickname.data:
                if letter not in nick_ok_letters:
                    return render_template('user/user.html', user=user_profile,
                                           form=form, he=current_user,
                                           error_msg=['There are restricted symbols in the username'],
                                           title='Redact profile')
            user_profile.nickname = form.nickname.data

        this_email_exists = db_sess.query(User).filter(User.email == form.email.data).first()
        if this_email_exists:
            if this_email_exists.email != current_user.email:
                return render_template('user/user.html', user=user_profile,
                                       form=form, he=current_user,
                                       error_msg=['That email is taken. Please choose a different one.'],
                                       title='Redact profile')
            else:
                user_profile.email = form.email.data
        else:
            user_profile.email = form.email.data
        user_profile.name = form.name.data
        user_profile.surname = form.surname.data
        db_sess.add(user_profile)
        db_sess.commit()
        flash('Your account has been updated!', 'success')
        return redirect(f'/users/{form.nickname.data}')
    return redirect(f"/users/{nickname}")


@app.route('/all_data_files')
def all_data_files():
    files_list = []
    for file_name in os.listdir('static/mat/'):
        if not file_name.endswith('.mat') or file_name.startswith("."):
            continue
        abs_path = os.path.abspath(os.path.join('static/mat/', file_name))
        print("Abs path is", abs_path)
        bytes_size = os.path.getsize(abs_path)
        norm_syze: str = human_readable_file_size(bytes_size)
        files_list.append((file_name, norm_syze, abs_path))
    files_list.sort(key=lambda _: _[0], reverse=True)
    return render_template('all_data_files.html', files_list=files_list, count=1, he=current_user,
                           title='All PGI files')


if __name__ == "__main__":
    # app.run('0.0.0.0', port=5000, debug=True)
    app.run('127.0.0.1', port=5000, debug=True)
    # serve(app, host='0.0.0.0', port=5000)
    if server:
        server.quit()
