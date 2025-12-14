from flask import render_template
from flask_login import login_required, current_user
from . import users_bp

from app.models import WordList, QuizResult

@users_bp.route("/profile")
@login_required
def profile():
    user = current_user
    wordlists = WordList.query.filter_by(user_id=user.id).all()

    total_words = sum(len(wl.words) for wl in wordlists)
    total_lists = len(wordlists)

    quizzes = QuizResult.query.filter_by(user_id=user.id).order_by(QuizResult.date).all()

    hardest = []
    for wl in wordlists:
        for w in wl.words:
            hardest.append({
                "original": w.original,
                "wrong_count": getattr(w, "wrong_count", 0),
                "correct_count": getattr(w, "correct_count", 0),
                "last_wrong": w.last_wrong.strftime("%d %b") if getattr(w, "last_wrong", None) else "–",
            })

    hardest.sort(key=lambda x: x["wrong_count"], reverse=True)

    return render_template(
        "profile.html",
        user=user,
        total_words=total_words,
        total_lists=total_lists,
        total_quizzes=len(quizzes),
        quiz_labels=[q.date.strftime("%d %b") for q in quizzes],
        quiz_scores=[q.correct_count for q in quizzes],
        hardest_words=hardest,
    )

@users_bp.route("/stats")
@login_required
def stats():
    user = current_user

    # Hämtar statistik
    total_lists = WordList.query.filter_by(user_id=user.id).count()
    total_words = Word.query.join(WordList).filter(WordList.user_id == user.id).count()
    total_quizzes = QuizResult.query.filter_by(user_id=user.id).count()

    # Resultat över tid (till grafen)
    quiz_results = QuizResult.query.filter_by(user_id=user.id).order_by(QuizResult.date).all()
    quiz_labels = [q.date.strftime("%Y-%m-%d") for q in quiz_results]
    quiz_scores = [q.correct_count for q in quiz_results]

    # Svåraste ord (fel-sorterad topplista)
    hardest_words = (
        Word.query
        .join(WordList)
        .filter(WordList.user_id == user.id)
        .filter(Word.wrong_count > 0)
        .order_by(Word.wrong_count.desc())
        .limit(20)
        .all()
    )

    return render_template(
        "users/stats.html",
        user=user,
        total_lists=total_lists,
        total_words=total_words,
        total_quizzes=total_quizzes,
        quiz_labels=quiz_labels,
        quiz_scores=quiz_scores,
        hardest_words=hardest_words
    )
