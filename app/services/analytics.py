from datetime import datetime, timedelta
from app.models import QuizAnswerLog, Word, WordList
from app.extensions import db


def get_word_statistics(user_id):
    """
    Returnerar statistik för alla ord:
    - total number of attempts
    - correct attempts
    - wrong attempts
    - last wrong date
    """

    logs = (
        QuizAnswerLog.query
        .filter_by(user_id=user_id)
        .all()
    )

    stats = {}

    for log in logs:
        if log.word_id not in stats:
            stats[log.word_id] = {
                "word_id": log.word_id,
                "correct": 0,
                "wrong": 0,
                "last_wrong": None,
            }

        if log.is_correct:
            stats[log.word_id]["correct"] += 1
        else:
            stats[log.word_id]["wrong"] += 1
            stats[log.word_id]["last_wrong"] = log.timestamp

    return stats


def get_hardest_words(user_id, limit=20):
    """
    Returnerar användarens svåraste ord baserat på:
    - flest fel
    - senast felaktigt svar
    """

    stats = get_word_statistics(user_id)

    # Gör om till lista + hämta ordens text
    result = []
    for word_id, s in stats.items():
        word = Word.query.get(word_id)
        if not word:
            continue

        result.append({
            "original": word.original,
            "translation": word.translation,
            "correct": s["correct"],
            "wrong": s["wrong"],
            "last_wrong": s["last_wrong"].strftime("%d %b") if s["last_wrong"] else "–",
        })

    # sortera på flest fel
    result.sort(key=lambda x: x["wrong"], reverse=True)

    return result[:limit]

def get_quiz_history(user_id):
    """Returnerar resultat per datum."""
    logs = (
        QuizAnswerLog.query
        .filter_by(user_id=user_id)
        .order_by(QuizAnswerLog.timestamp.asc())
        .all()
    )

    by_day = {}

    for log in logs:
        day = log.timestamp.strftime("%Y-%m-%d")

        if day not in by_day:
            by_day[day] = {"correct": 0, "wrong": 0}

        if log.is_correct:
            by_day[day]["correct"] += 1
        else:
            by_day[day]["wrong"] += 1

    result = []
    for day, v in by_day.items():
        total = v["correct"] + v["wrong"]
        accuracy = round((v["correct"] / total) * 100, 1) if total else 0

        result.append({
            "date": day,
            "correct": v["correct"],
            "wrong": v["wrong"],
            "accuracy": accuracy,
        })

    return result

from datetime import datetime, timedelta

def get_daily_streaks(user_id):
    """Returnerar nuvarande streak och längsta streak."""
    logs = (
        QuizAnswerLog.query
        .filter_by(user_id=user_id)
        .order_by(QuizAnswerLog.timestamp.asc())
        .all()
    )

    if not logs:
        return {"current": 0, "longest": 0}

    # extrahera unika dagar
    days = sorted({log.timestamp.date() for log in logs})

    longest = 1
    current = 1

    for i in range(1, len(days)):
        prev = days[i - 1]
        curr = days[i]

        if curr == prev + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    # kolla om streaken bröts idag
    if days[-1] != datetime.utcnow().date():
        current = 0

    return {"current": current, "longest": longest}

