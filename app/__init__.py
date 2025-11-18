import os
from flask import Flask
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer

from .extensions import db, mail, migrate
from .models import User

from dotenv import load_dotenv
load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "main.login"


def create_app():
    app = Flask(__name__)

    # SECRET KEY
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

    # DATABASE: Railway Postgres eller lokal SQLite
    if os.environ.get("DATABASE_URL"):
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            print("⚠️ VARNING: DATABASE_URL saknas! Använder SQLite temporärt.")
            database_url = "sqlite:///site.db"

        # 👉 ALWAYS convert to pg8000 driver
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql+pg8000://"
            )
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+pg8000://"
            )
        elif database_url.startswith("postgresql+psycopg2://"):
            database_url = database_url.replace(
                "postgresql+psycopg2://", "postgresql+pg8000://"
            )

        app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    else:
        # Lokal utveckling
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # MAIL SETTINGS
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "nygander.user@gmail.com"
    app.config["MAIL_PASSWORD"] = "vdpstiqklryzzvwh"

    # INIT EXTENSIONS
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.serializer = URLSafeTimedSerializer(app.secret_key)

    # BLUEPRINTS
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # AUTO-CREATE TABLES
    with app.app_context():
        db.create_all()

    return app
