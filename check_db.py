from app import create_app
from app.extensions import db
from app.models import Word

app = create_app()

with app.app_context():
    words = Word.query.all()
    for w in words[:20]:
        print(w.original, "=>", w.translation)
