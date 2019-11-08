from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app import data
from app.tools import get_season_week
import json
import requests
import pandas as pd


games = db.Table(
    'games',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    game = db.relationship(
        'User', secondary=games,
        primaryjoin=(games.c.user_id == id),
        secondaryjoin=(games.c.game_id == id),
        backref=db.backref('games', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Week(db.Model):
    number = db.Column(db.Integer)
    start = db.DateTimeProperty()
    end = db.DateTimeProperty()
    games = db.relationship('Game')


    def __init__(self, week, start, end):
        self.number = get_season_week()[1]
        self.start = start
        self.end = end
    def add_games(self, week):
        games_of_the_week = data.main(get_season_week()[1])
        for row, index in games_of_the_week.iteritems():
            game = Game(game_id = row['id'], home_team=row['homeTeam'], away_team=row['awayTeam'], away_rank=row['awayRank'],
                        home_rank=row['homeRank'])
            db.session.add(game)
            db.session.commit()

    def update_scores(week):
        data = requests.get(url.format(week=week))
        d = json.loads(data.text)
        events = d.get('events')[0]
        competitions = events.get('competitions')[0]
        for competitions in d.get('events'):
            game = Game.query.filter(week=week).filter(id=competitions['id']).first()
            competition = competitions.get('competitions')[0]
            competitors = competition.get('competitors')
            game.away_score = competitors[1].get('score')
            game.home_score = competitors[0].get('score')
            db.session.add(game)
            db.session.commit()



class Game(db.Model):
    id = db.Column(db.Integer)
    week = db.Column(db.Integer)
    user_id = db.realationship()
    home_team = db.Column(db.String)
    home_rank = db.Column(db.Integer)
    away_team = db.Column(db.String)
    away_rank = db.Column(db.Integer)
    pick = db.Column(db.String)
    winner = db.Column(db.String)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)

    def __repr__(self):
        return '<Home:{} - {} Away:{} - {}>'.format(self.home_team, self.home_score, self.away_team, self.away_score)

    def __init__(self, game_id, home_team, away_team, away_rank, home_rank):
        self.id = game_id
        self.week = get_season_week()[1]
        self.home_team = home_team
        self.away_team = away_team
        self.away_rank = away_rank
        self.home_rank = home_rank
        self.home_score = 0
        self.away_score = 0

    def add_win(self, user_id):
        user = User.query_all(user_id == user_id)
        user.wins = user.wins+1
        db.Session.add(user)
        db.Session.commit()


    # def who_won(self):




