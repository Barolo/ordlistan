import json
from app import create_app
from app.extensions import db
from app.models import User, WordList, Word, QuizResult
from datetime import datetime

app = create_app()

with app.app_context():
    with open("sqlite_export.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # töm postgres först (valfritt)
    db.session.query(QuizResult).delete()
    db.session.query(Word).delete()
    db.session.query(WordList).delete()
    db.session.query(User).delete()
    db.session.commit()

    # användare
    for u in data["users"]:
        user = User(id=u["id"], username=u["username"], email=u["email"], password=u["password"])
        db.session.add(user)

    db.session.commit()

    # listor
    for wl in data["wordlists"]:
        list_obj = WordList(id=wl["id"], name=wl["name"], user_id=wl["user_id"])
        db.session.add(list_obj)

    db.session.commit()

    # ord
    for w in data["words"]:
        word = Word(
            id=w["id"],
            original=w["original"],
            translation=w["translation"],
            correct_count=w["correct_count"],
            wrong_count=w["wrong_count"],
            last_wrong=datetime.fromisoformat(w["last_wrong"]) if w["last_wrong"] else None,
            list_id=w["list_id"]
        )
        db.session.add(word)

    db.session.commit()

    # quizresultat
    for r in data["results"]:
        result = QuizResult(
            id=r["id"],
            user_id=r["user_id"],
            correct_count=r["correct_count"],
            total_questions=r["total_questions"],
            date=datetime.fromisoformat(r["date"])
        )
        db.session.add(result)

    db.session.commit()

print("Import klar — PostgreSQL innehåller nu samma data som SQLite!")
