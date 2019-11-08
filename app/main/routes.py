from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User, Week, Game
from app.main import bp
import json
from app.tools import get_season_week

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/index')
@login_required
def index():
    user = current_user
    week = get_season_week()[1]
    games = Game.query.filter_by(week=week)
    if games is None:
        week = Week(week)
        week.add_games(num_week)
        games = Game.query.filter_by(week=num_week)
    update_scores()
    if current_user.is_authenticated:
        if current_user.confirmed:
            return render_template('index.html', user=user, title='Home')
        else:
            return redirect(url_for('auth.unconfirmed'))
    return render_template('index.html', user=user, title='Home')



@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    quals = user.qualifications
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return render_template('user.html', title='User',
                               form=form, user=user)
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('user.html', title='User',
                           form=form, user=user)