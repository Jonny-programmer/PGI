import smtplib
import mimetypes
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(email_user, subject, subject_admins, text, text_admins, admins=None, attachments=None):
    addr_from = os.getenv('FROM')
    password = os.getenv('PASSWORD')
    server = smtplib.SMTP_SSL(os.getenv('HOST'), os.getenv('PORT'))
    server.login(addr_from, password)

    # Письмо номер 1 (пользователю)
    msg1 = MIMEMultipart()
    msg1['From'] = addr_from
    msg1['To'] = email_user
    msg1['Subject'] = subject

    msg1.attach(MIMEText(text, 'plain'))
    # Отправка эл. письма пользователю
    server.send_message(msg1)

    # Письмо номер 2 (админам)
    if not admins:
        server.quit()
        return True
    for mail_addr in admins:
        msg2 = MIMEMultipart()
        msg2['From'] = addr_from
        msg2['Subject'] = subject_admins
        msg2['To'] = mail_addr
        msg2.attach(MIMEText(text_admins, 'plain'))

        server.send_message(msg2)

    server.quit()
    return True
