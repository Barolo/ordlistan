import os
from flask import Flask
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer

from .extensions import db, mail, migrate
from .models import User


login_manager = LoginManager()
login_manager.login_view = 'main.login'


def create_app():
    app = Flask(__name__)

    # -------------------------------------------------
    # SECRET KEY
    # -------------------------------------------------
    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

    # -------------------------------------------------
    # DATABASE (Railway Postgres eller lokal SQLite)
    # -------------------------------------------------
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        # === Railway Mode ===
        database_url = os.environ.get("DATABASE_URL")  # sätts automatiskt av Railway

        # Railway behöver psycopg-format
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace(
            "postgres://", "postgresql+psycopg://"
        )

    else:
        # === Lokal utveckling ===
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # -------------------------------------------------
    # MAIL SETTINGS
    # -------------------------------------------------
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'nygander.user@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vdpstiqklryzzvwh'

    # -------------------------------------------------
    # INIT EXTENSIONS
    # -------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Serializer för lösenordsreset
    app.serializer = URLSafeTimedSerializer(app.secret_key)

    # -------------------------------------------------
    # BLUEPRINTS
    # -------------------------------------------------
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # -------------------------------------------------
    # AUTO-CREATE TABLES (Railway + lokalt)
    # -------------------------------------------------
    with app.app_context():
        db.create_all()

    return app
