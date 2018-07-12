from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from . import au
from .email import send_password_reset_email
from .forms import LoginForm, RegisterForm, ResetPasswordForm, ResetPasswordRequestForm
from .. import db
from ..models import User


@au.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return(redirect(url_for('/')))
	form_obj = LoginForm()
	# Whent the browser sends a POST request as a result of the user pressing the submit buttom, form.validate_on_submit() 
	# is going to gather all the data, run all validators attached to fields, and if everything is all right it will return True
	if form_obj.validate_on_submit():
		flash('Login requested for user {}, remember_me={}'.format(form_obj.username.data, form_obj.remember_me.data))
		user = User.query.filter_by(username=form_obj.username.data).first()
		if user is None or not user.check_password(form_obj.password.data):
			flash('Invalid username or password')
			return(redirect(url_for('auth.login')))
		# login_user() comes from flask_login extension. This function will register the user as logged in, so that means
		# that any future pages the user navigates to will have the current_user set to that user.
		login_user(user,remember=form_obj.remember_me.data)	
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('main.home')
		return(redirect(next_page))
	return(render_template('login.html', form = form_obj))

@au.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return(redirect(url_for('home')))
	rform = RegisterForm()
	if rform.validate_on_submit():
		user = User(username = rform.username.data, email = rform.email.data)
		user.set_password(rform.password.data)
		db.session.add(user)
		db.session.commit()
		flash('You are registered. ¡Now you can login to have access to our amazing things!')
		return(redirect(url_for('auth.login')))

	return(render_template('register.html', form=rform))

@au.route('/logout')
@login_required
def logout():
	logout_user()
	return(redirect(url_for('main.home')))

@au.route('/reset_password_request', methods = ['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return(redirect(url_for('auth.login')))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash('Check your email for the instructions to reset your password')
		return(redirect(url_for('auth.login')))
	return(render_template('reset_password_request.html', title = 'Reset Password', form = form))

@au.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)
