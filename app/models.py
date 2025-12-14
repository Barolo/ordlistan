from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationer
    word_lists = db.relationship('WordList', backref='user', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

    # Password helpers
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def find_by_identifier(cls, identifier):
        return cls.query.filter(
            (cls.username == identifier) |
            (cls.email == identifier)
        ).first()



class WordList(db.Model):
    __tablename__ = 'word_list'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    words = db.relationship(
        'Word',
        backref='word_list',
        lazy=True,
        cascade="all, delete-orphan"
    )


class Word(db.Model):
    __tablename__ = 'word'

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(255), nullable=False)
    translation = db.Column(db.String(255), nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    wrong_count = db.Column(db.Integer, default=0)
    last_wrong = db.Column(db.DateTime)

    is_global = db.Column(db.Boolean, default=False)

    list_id = db.Column(db.Integer, db.ForeignKey('word_list.id'), nullable=False)


class QuizResult(db.Model):
    __tablename__ = 'quiz_result'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    correct_count = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class PublicWord(db.Model):
    __tablename__ = 'public_word'

    id = db.Column(db.Integer, primary_key=True)
    swedish = db.Column(db.String(255), nullable=False)
    english = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # easy / medium / hard


class QuizAnswerLog(db.Model):
    __tablename__ = "quiz_answer_log"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_result_id = db.Column(db.Integer, db.ForeignKey("quiz_result.id"), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), nullable=False)

    user_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationer
    user = db.relationship("User", backref="answer_logs", lazy=True)
    quiz_result = db.relationship("QuizResult", backref="answer_logs", lazy=True)
    word = db.relationship("Word", backref="answer_logs", lazy=True)
