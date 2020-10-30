from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from SV.models import User


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField(
        'Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register!')

    def validate_email(self, field):
        # Check if not None for that user email!
        if User.query.filter_by(email=field.data).first():
            print("email taken")
            raise ValidationError('Your email has been registered already!')

    def validate_username(self, field):
        # Check if not None for that username!
        if User.query.filter_by(username=field.data).first():
            print("username taken")
            raise ValidationError('Sorry, that username is taken!')

