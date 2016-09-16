from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('输入您的邮箱地址:', validators=[DataRequired(message='请输入邮箱'),
                                                 Length(1, 64, message='邮箱最大字符不能64'), Email()])
    password = PasswordField('输入您的密码：', validators=[DataRequired(message='请输入密码')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    username = StringField('输入您的用户名:', validators=[DataRequired(), Length(0, 8)])
    password = PasswordField('设置您的密码:', validators=[DataRequired(message='请输入新密码'), EqualTo('password2',
                                                                                    message='输入的两次新密码必须一致.')])
    password2 = PasswordField('再次输入您设置的密码:', validators=[DataRequired(message='请再次输入新密码')])
    email = StringField('输入您注册的邮箱:', validators=[Email(), DataRequired(), Length(1, 64)])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('User name already exists.')


class ChangePasswordFrom(Form):
    oldpassword = PasswordField('原始密码：', validators=[DataRequired()])
    password = PasswordField('设置您的新密码:', validators=[DataRequired(message='输入新密码'), EqualTo('password2',
                                                                        message='输入的两次新密码必须一致.')])
    password2 = PasswordField('设置您的新密码:', validators=[DataRequired(message='请再次输入新密码')])
    submit = SubmitField('确定')


class ResetPasswordRequestForm(Form):
    email = StringField('您的注册邮箱:', validators=[Email(), DataRequired()])
    submit = SubmitField('确定')


class ResetPasswordForm(Form):
    email = StringField('您的注册邮箱：', validators=[Email(), DataRequired()])
    password = PasswordField('设置您的新密码:', validators=[DataRequired(), EqualTo('password2',
                                                                        message='输入的两次新密码必须一致.')])
    password2 = PasswordField('设置您的新密码:', validators=[DataRequired()])
    submit = SubmitField('确定')


class ChangeEmailForm(Form):
    email = StringField('设置您的新邮箱：', validators=[DataRequired(message='请输入新邮箱'), Email(message='不是邮箱格式')])
    password = PasswordField('输入您的密码：', validators=[DataRequired()])
    submit = SubmitField('确定')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('该邮箱已注册')
