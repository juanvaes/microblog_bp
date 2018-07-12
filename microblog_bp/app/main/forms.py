from flask_wtf import FlaskForm		#FlaskForm is the base class
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length


class PostForm(FlaskForm):
	post = TextAreaField('Write something', validators=[DataRequired(),Length(min=1, max=140)])
	submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
	submit = SubmitField('Submit')