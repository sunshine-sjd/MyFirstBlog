from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class NameForm(Form):
    name = StringField('Input your name:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[DataRequired(), Length(0, 64)])
    location = StringField('Location', validators=[DataRequired(), Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('email', validators=[DataRequired(), Length(0, 64),
                                             Email()])
    username = StringField('username', validators=[DataRequired(), Length(0, 64),
                                                   ])
    confirmed = BooleanField('confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[DataRequired(), Length(0, 64)])
    location = StringField('Location', validators=[DataRequired(), Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() and \
                field.data != self.user.email:
            raise ValidationError('Email has already exist.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() and \
                field.data != self.user.username:
            raise ValidationError('uername has already exist.')


class PostForm(Form):
    title = StringField('文章标题：', validators=[DataRequired(message='请输入文字...'),
                                             Length(0, 10, message='文章字数请限制10字以内')])
    body = PageDownField("记录你的点滴...", validators=[DataRequired(message='请输入文字...')])
    category = SelectField('文章分类：', choices=[('Python', 'Python'), ('Flask', 'Flask'), ('HTML&CSS', 'HTML&CSS'),
                                             ('算法', '算法'), ('数据库', '数据库')], coerce=str)
    submit = SubmitField('submit')


class EditPostForm(Form):
    body = PageDownField("记录你的点滴...", validators=[DataRequired()])
    submit = SubmitField('confirm change')


class CommentForm(Form):
    body = PageDownField("评论：", validators=[DataRequired()])
    submit = SubmitField('Submit')