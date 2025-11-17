import json
from app import create_app
from app.extensions import db
from app.models import User, WordList, Word, QuizResult

app = create_app()

with app.app_context():
    data = {
        "users": [],
        "wordlists": [],
        "words": [],
        "results": []
    }

    data["users"] = [
        {"id": u.id, "username": u.username, "email": u.email, "password": u.password}
        for u in User.query.all()
    ]

    data["wordlists"] = [
        {"id": w.id, "name": w.name, "user_id": w.user_id}
        for w in WordList.query.all()
    ]

    data["words"] = [
        {"id": w.id, "original": w.original, "translation": w.translation,
         "correct_count": w.correct_count, "wrong_count": w.wrong_count,
         "last_wrong": str(w.last_wrong) if w.last_wrong else None,
         "list_id": w.list_id}
        for w in Word.query.all()
    ]

    data["results"] = [
        {"id": r.id, "user_id": r.user_id, "correct_count": r.correct_count,
         "total_questions": r.total_questions, "date": str(r.date)}
        for r in QuizResult.query.all()
    ]

    with open("sqlite_export.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

print("Export klar — filen heter sqlite_export.json")
