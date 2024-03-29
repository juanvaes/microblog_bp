# Explanation
# db.Model is a base class for all models in flask-sqalchemy, and define fields as class variables
# fields of the database are created from db.Column class

from flask import current_app, url_for
from sqlalchemy import Column, ForeignKey, Integer, String
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
import base64
import os

from . import app
from . import db
from . import login

# Auxiliary table for creating followers/followed
followers = db.Table('followers', 
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), 
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, True)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page = page, per_page = per_page, **kwargs),
                'next': url_for(endpoint, page = page + 1, per_page = per_page, **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page = page - 1, per_page = per_page, **kwargs) if resources.has_prev else None
            }
        }
        return data

class User(PaginatedAPIMixin, UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index = True, unique=True)
    password = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User', secondary=followers, 
        primaryjoin=(followers.c.follower_id == id), 
        secondaryjoin=(followers.c.followed_id == id), 
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    # Token attributes
    token = db.Column(db.String(32), index = True, unique = True)
    token_expiration = db.Column(db.DateTime)

    # METHODS
    # This method tells python how to print objects of a class. It is useful for debugging.
    def __repr__(self):
        return ('<User {}>'.format(self.username))


    def set_password(self,password_in):
        self.password = generate_password_hash(password_in)


    def check_password(self,password_in):
        return (check_password_hash(self.password,password_in))


    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return ('https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size))


    # for handling followers/followed	
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)


    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)


    def is_following(self, user):
        return (self.followed.filter(followers.c.followed_id == user.id).count() > 0)


    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return(followed.union(own).order_by(Post.timestamp.desc()))
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], 
            algorithm = 'HS256').decode('utf-8')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithm = ['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)


    def to_dict(self, include_emaill = True):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen,
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'followers_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id = self.id),
                'followers': url_for('api.get_followers', id = self.id),
                'followed': url_for('api.get_followed', id = self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_emaill:
            data['email'] = self.email
        return data
    
    def from_dict(self, data, new_user = False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
            if new_user and 'password' in data:
                self.set_password(data['password'])	
    
    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(secondes=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('urf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    
    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token = token).first()
        if user is None or usen.token_expiration < datetime.utcnow():
            return None
        return user


class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lan = db.Column(db.String(5))


    def __repr__(self):
        return '<Post {}>'.format(self.body)







