import logging
from logging.config import fileConfig

from alembic import context
from app import create_app, db

# Alembic config object
config = context.config

# Setup logging from alembic.ini
import os
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
fileConfig(config_path)
logger = logging.getLogger('alembic.env')


def get_engine():
    """Returnerar SQLAlchemy engine från Flask app"""
    try:
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    """Returnerar connection URL"""
    try:
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


def get_metadata():
    """Returnerar metadata med alla modeller"""
    db = current_app.extensions['migrate'].db
    if hasattr(db, 'metadatas'):
        return db.metadatas[None]
    return db.metadata


def run_migrations_offline():
    """Offline migrations (genererar SQL utan connection)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    app = create_app()

    with app.app_context():
        connectable = db.engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=db.metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()

# Huvudkontroll
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
