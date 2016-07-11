from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('Input your email:', validators=[DataRequired(), Length(1, 64),
                                                         Email()])
    password = PasswordField('Input your password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    username = StringField('Input your username:', validators=[DataRequired(), Length(6, 8)])
    password = PasswordField('Input your password:', validators=[DataRequired(), EqualTo('password2',
                                                                                    message='password must match.')])
    password2 = PasswordField('Input your password again:', validators=[DataRequired()])
    email = StringField('Input your email:', validators=[Email(), DataRequired(), Length(1, 64)])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('User name already exists.')


class ChangePasswordFrom(Form):
    oldpassword = PasswordField('Your old password', validators=[DataRequired()])
    password = PasswordField('Input your new password:', validators=[DataRequired(), EqualTo('password2',
                                                                        message='password must match.')])
    password2 = PasswordField('Input your new password again:', validators=[DataRequired()])
    submit = SubmitField('submit')


class ResetPasswordRequestForm(Form):
    email = StringField('Your email:', validators=[Email(), DataRequired()])
    submit = SubmitField('submit')


class ResetPasswordForm(Form):
    email = StringField('Your email', validators=[Email(), DataRequired()])
    password = PasswordField('Input your new password:', validators=[DataRequired(), EqualTo('password2',
                                                                        message='password must match.')])
    password2 = PasswordField('Input your new password again:', validators=[DataRequired()])
    submit = SubmitField('submit')


class ChangeEmailForm(Form):
    email = StringField('new email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email has already exists.')
