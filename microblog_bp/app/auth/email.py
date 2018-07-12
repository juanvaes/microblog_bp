from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from . import au
from ..email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[OPEN Blog] Reset Your Password',
       sender = current_app.config['ADMINS'][0],
       recipients = [user.email],
       text_body = render_template('reset_password.txt', user = user,token = token),
       html_body = render_template('reset_password_msg.html', user = user,token = token))
    