from flask import render_template, redirect, url_for, request, flash
from .forms import LoginForm, RegistrationForm, ChangePasswordFrom, ResetPasswordRequestForm, ResetPasswordForm
from .forms import ChangeEmailForm
from . import auth
from ..models import User
from flask_login import login_user, login_required, logout_user, current_user
from .. import db
from ..email import send_email
from datetime import datetime


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and \
                request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid user or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have sign out!')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data,
                    member_since=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'confirm email', 'auth/email/confirm', user=user, token=token)
        flash('Confirm email has sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account, thanks.')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account','auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordFrom()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpassword.data):
            if form.password.data != form.oldpassword.data:
                current_user.password = form.password.data
                db.session.add(current_user)
                flash('You have changed your password.')
                return redirect(url_for('main.index'))
            else:
                flash('new password must be different from old password.')
        else:
            flash('Invalid old password.')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(to=form.email.data, subject='Reset-password-request', template='auth/email/reset_password',
                        user=current_user, token=token)
            flash('Reset password email have been sent.')
        else:
            flash('Invalid email')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.reset_password(token, form.password.data):
            flash('You have reset your password.')
            return redirect(url_for('auth.login'))
        if user is None:
            return redirect(url_for('main.index'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email-request', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            token = current_user.generate_email_change_token(new_email=form.email.data)
            send_email(to=form.email.data, subject='Change email', template='auth/email/change_email',
                       user=current_user, token=token)
            flash('Change email request have been sent to your new email.')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid password')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('You have changed your email')
    else:
        flash('Invalid request')
    return redirect(url_for('main.index'))