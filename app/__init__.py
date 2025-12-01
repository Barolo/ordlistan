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

    # -----------------------------
    # SECRET KEY
    # -----------------------------
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

    # -----------------------------
    # DATABASE CONFIG (AUTO SWITCH)
    # -----------------------------
    raw_db_url = os.environ.get("DATABASE_URL")

    if raw_db_url:
        # fall: DATABASE_URL finns men är tom sträng
        if raw_db_url.strip() == "":
            print("⚠️ DATABASE_URL är tom – använder lokal SQLite i stället.")
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
        else:
            db_url = raw_db_url

            # Railway använder psycopg2-format → vi tvingar pg8000
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
            elif db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
            elif db_url.startswith("postgresql+psycopg2://"):
                db_url = db_url.replace("postgresql+psycopg2://", "postgresql+pg8000://", 1)

            app.config["SQLALCHEMY_DATABASE_URI"] = db_url
            print("🌐 Kör på Railway/Postgres:", db_url)
    else:
        # ✨ Lokal utveckling
        print("💻 Ingen DATABASE_URL – kör SQLite lokalt.")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -----------------------------
    # MAIL SETTINGS
    # -----------------------------
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"

    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")

    if not mail_username or not mail_password:
        print("⚠️ MAIL_USERNAME eller MAIL_PASSWORD saknas – e-post skickas inte.")
        app.config["MAIL_SUPPRESS_SEND"] = True
    else:
        app.config["MAIL_USERNAME"] = mail_username
        app.config["MAIL_PASSWORD"] = mail_password

    # -----------------------------
    # INIT EXTENSIONS
    # -----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Serializer
    app.serializer = URLSafeTimedSerializer(app.secret_key)

    # -----------------------------
    # BLUEPRINTS
    # -----------------------------
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # -----------------------------
    # CREATE TABLES (LOCAL)
    # -----------------------------
    with app.app_context():
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            db.create_all()

    return app
