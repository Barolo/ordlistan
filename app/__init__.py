import os
from flask import Flask
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer

from .extensions import db, mail, migrate
from .models import User  # viktigt att detta importeras efter db


login_manager = LoginManager()
login_manager.login_view = 'main.login'


def create_app():
    app = Flask(__name__)

    # CONFIG
    app.secret_key = os.urandom(24)

    # SQLite, funkar både lokalt och på Render
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'nygander.user@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vdpstiqklryzzvwh'

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.serializer = URLSafeTimedSerializer(app.secret_key)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

        # Skapa alla tabeller automatiskt (även i Render)
    with app.app_context():
        db.create_all()

    return app
