from .extensions import db
from datetime import datetime
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # relationer
    word_lists = db.relationship('WordList', backref='user', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)


class WordList(db.Model):
    __tablename__ = 'word_list'   # MATCHAR DATABASEN

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    words = db.relationship('Word', backref='word_list', lazy=True)


class Word(db.Model):
    __tablename__ = 'word'

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(255), nullable=False)
    translation = db.Column(db.String(255), nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    wrong_count = db.Column(db.Integer, default=0)
    last_wrong = db.Column(db.DateTime)

    list_id = db.Column(db.Integer, db.ForeignKey('word_list.id'), nullable=False)


class QuizResult(db.Model):
    __tablename__ = 'quiz_result'   # MATCHAR DATABASEN

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    correct_count = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)