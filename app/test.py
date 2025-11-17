from app import create_app, db
from app.models import User, WordList, Word, QuizResult

app = create_app()

with app.app_context():
    print("Tables in metadata:", db.metadata.tables.keys())
