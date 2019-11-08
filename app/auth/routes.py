import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, \
    ResetPasswordForm, UpdateInfoForm
from app.auth.email import  send_confirmation_email, send_password_reset_email
from app.models import User, Qualification


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.confirmed:
            return redirect(url_for('main.index'))
        else:
            return redirect(url_for('auth.unconfirmed'))
    form = LoginForm()
    if form.validate_on_submit():
        ## allow sign in with username or email
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User.query.filter_by(email=form.username.data.lower()).first()
            if user is None:
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
            ## This should route them to unconfirmed.html
            return redirect(url_for('auth.login'))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('welcome.home')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)




@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login.html'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            confirmed=False,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_confirmation_email(user)
        login_user(user)
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/confirm_email/<token>', methods=['GET', 'POST'])
@login_required
def confirm_email(token):
    if current_user.confirmed:
        print ("already confirmed")
        return redirect(url_for('main.index'))
    user = User.confirm_token(token)
    if not user:
        return render_template('auth/unconfirmed.html')
    else:
        user.confirmed=True
        user.confirmed_on = datetime.datetime.now()
        db.session.commit()
        return redirect(url_for('main.index'))



@bp.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('main.index')

    return render_template('auth/unconfirmed.html')

@bp.route('/resend_confirmation')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        return redirect('main.index')
    send_confirmation_email(current_user)
    flash('A new confirmation link has been sent to your email', 'warning')
    return render_template('auth/unconfirmed.html')

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password Request', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
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
        flash(('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Reset Password', form=form)
