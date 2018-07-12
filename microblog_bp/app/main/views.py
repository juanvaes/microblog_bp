from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from guess_language import guessLanguage
from datetime import datetime

from . import mn
from .forms import PostForm, EditProfileForm
from .. import db
from ..models import Post, User
from .. import app



@mn.route('/', methods=['GET','POST']) 
@mn.route('/home', methods=['GET','POST'])
#@login_required
def home():
    form_obj = PostForm()
    if form_obj.validate_on_submit():
        # Funcionality to guees de language of submitted post
        lan = guessLanguage(form_obj.post.data)
        print(lan)
        if lan == 'UNKNOWN' or len(lan) > 5:
            lan = ''
        post= Post(body=form_obj.post.data, author=current_user, lan = lan)
        db.session.add(post)
        db.session.commit()
        flash('Great!')
        return redirect(url_for('main.home'))
    page = request.args.get('page', 1, type = int)
    if current_user.is_authenticated:
        posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
        # Next url
        next_url = url_for('main.home', page = posts.next_num) if posts.has_next else None
        prev_url = url_for('main.home', page = posts.prev_num) if posts.has_prev else None
        return(render_template('home.html', title = 'Home', form = form_obj, posts = posts.items, next_url = next_url, prev_url = prev_url))
    
    return(render_template('home.html', title = 'Explore', form = form_obj))

@mn.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type = int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page = posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page = posts.prev_num) if posts.has_prev else None
	return render_template('home.html', title = 'Explore', posts = posts.items, next_url = next_url, prev_url = prev_url)

@mn.route('/user/<username>')
@login_required
def user_profile(username):
	user = User.query.filter_by(username=username).first_or_404()
	current_seen = datetime.utcnow()
	last_seen = user.last_seen
	page = request.args.get('page', 1, type = int)
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.user_profile', username = user.username, page = posts.next_num) if posts.has_next else None
	prev_url = url_for('main.user_profile', username = user.username, page = posts.prev_num) if posts.has_prev else None
	return(render_template('user.html', user = user, posts = posts.items, next_url = next_url, prev_url = prev_url, last_seen=last_seen, current_seen = current_seen))

@mn.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@mn.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form_obj = EditProfileForm()
    if form_obj.validate_on_submit():
        current_user.username = form_obj.username.data
        current_user.about_me = form_obj.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return(redirect(url_for('main.edit_profile')))
    elif request.method == 'GET':
        form_obj.username.data = current_user.username
        form_obj.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title = 'Edit Profile', form=form_obj)


@mn.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	print(user)
	if user is None:
		flash('User {} not found'.format(username))
		return(redirect(url_for('main.home')))
	if user == current_user:
		flash('You can not follow yourself')
		return(redirect(url_for('main.user_profile', username=username)))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return(redirect(url_for('main.user_profile', username = username)))


@mn.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found'.format(username))
		return(redirect(url_for('main.home')))
	if user == current_user:
		flash('You can not unfollow yourself')
		return(redirect(url_for('main.user_profile', username=username)))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following {}!'.format(username))
	return(redirect(url_for('main.user_profile', username=username)))


@mn.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
	return(render_template('dashboard.html'))