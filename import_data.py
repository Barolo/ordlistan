import csv
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models import User, WordList, Word, QuizResult

CSV_PATH = "db/"

app = create_app()

def fix(s):
    """Fixar mojibake som 'BÃ¥t' -> 'Båt'"""
    if s is None:
        return None
    try:
        # Konvertera cp1252 -> bytes -> utf-8
        return s.encode("cp1252", errors="ignore").decode("utf-8", errors="ignore")
    except:
        return s

def import_users():
    print("Importing users...")
    with open(CSV_PATH + "user.csv", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = User(
                id=int(row["id"]),
                username=fix(row["username"]),
                email=fix(row["email"]),
                password=row["password"]  # password ska inte fixas
            )
            db.session.merge(user)
    db.session.commit()
    print("Users imported.")

def import_word_lists():
    print("Importing word lists...")
    with open(CSV_PATH + "word_list.csv", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:

            created_at = None
            if row.get("created_at") and row["created_at"].strip():
                try:
                    created_at = datetime.fromisoformat(row["created_at"])
                except:
                    try:
                        created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
                    except:
                        created_at = None

            wl = WordList(
                id=int(row["id"]),
                name=fix(row["name"]),
                user_id=int(row["user_id"]),
                created_at=created_at
            )
            db.session.merge(wl)
    db.session.commit()
    print("Word lists imported.")

def import_words():
    print("Importing words...")
    with open(CSV_PATH + "word.csv", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:

            last_wrong = None
            if row.get("last_wrong") and row["last_wrong"].strip():
                try:
                    last_wrong = datetime.fromisoformat(row["last_wrong"])
                except:
                    last_wrong = None

            word = Word(
                id=int(row["id"]),
                original=fix(row["original"]),
                translation=fix(row["translation"]),
                correct_count=int(row["correct_count"]),
                wrong_count=int(row["wrong_count"]),
                last_wrong=last_wrong,
                list_id=int(row["list_id"])
            )
            db.session.merge(word)
    db.session.commit()
    print("Words imported.")

def import_quiz_results():
    print("Importing quiz results...")
    with open(CSV_PATH + "quiz_result.csv", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:

            date_val = None
            if row.get("date") and row["date"].strip():
                try:
                    date_val = datetime.fromisoformat(row["date"])
                except:
                    try:
                        date_val = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
                    except:
                        date_val = None

            qr = QuizResult(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                correct_count=int(row["correct_count"]),
                total_questions=int(row["total_questions"]),
                date=date_val
            )
            db.session.merge(qr)
    db.session.commit()
    print("Quiz results imported.")

def run_all_imports():
    with app.app_context():
        import_users()
        import_word_lists()
        import_words()
        import_quiz_results()
        print("\nAll CSV data imported successfully!\n")

if __name__ == "__main__":
    run_all_imports()
