import os
from flask import Flask
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer

from dotenv import load_dotenv
load_dotenv()

from app.extensions import db, mail, migrate
from app.models import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"     # vart användare skickas om ej inloggad


def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # SECRET KEY
    # --------------------------------------------------
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

    # --------------------------------------------------
    # DATABASE CONFIG (Auto-switch SQLite ↔ Railway)
    # --------------------------------------------------
    raw_db_url = os.getenv("DATABASE_URL")

    if raw_db_url:
        db_url = raw_db_url.strip()

        if not db_url:
            print("⚠️ DATABASE_URL är tom – använder SQLite lokalt.")
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
        else:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
            elif db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
            elif db_url.startswith("postgresql+psycopg2://"):
                db_url = db_url.replace("postgresql+psycopg2://", "postgresql+pg8000://", 1)

            print("🌐 Kör på Railway/Postgres:", db_url)
            app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    else:
        print("💻 Ingen DATABASE_URL – kör lokalt med SQLite.")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------------------------------------
    # PG8000 — auto reconnect
    # --------------------------------------------------
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 180,
    }

    # --------------------------------------------------
    # MAIL SETTINGS
    # --------------------------------------------------
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    if not mail_username or not mail_password:
        print("⚠️ MAIL-konfiguration saknas – mail kommer inte skickas.")
        app.config["MAIL_SUPPRESS_SEND"] = True
    else:
        app.config["MAIL_USERNAME"] = mail_username
        app.config["MAIL_PASSWORD"] = mail_password

    # --------------------------------------------------
    # INIT EXTENSIONS
    # --------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Serializer till lösenordsreset
    app.serializer = URLSafeTimedSerializer(app.secret_key)

    # --------------------------------------------------
    # BLUEPRINTS
    # --------------------------------------------------
    from app.auth.routes import auth_bp
    from app.public.routes import public_bp
    from app.dashboard.routes import dashboard_bp
    from app.lists.routes import lists_bp
    from app.quiz.routes import quiz_bp
    from app.admin import admin_bp
    from app.users import users_bp
    from app.settings import settings_bp
    from app.stats import stats_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(stats_bp)

    # --------------------------------------------------
    # CREATE TABLES LOCALLY (SQLite only)
    # --------------------------------------------------
    with app.app_context():
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            db.create_all()

    return app
