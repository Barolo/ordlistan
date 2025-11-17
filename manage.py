from flask.cli import FlaskGroup
from app import create_app
from app.extensions import db
from app import models  # Viktigt: importera modellerna så Flask-Migrate ser dem

app = create_app()
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
