from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import WordList, QuizResult
from app.dashboard import dashboard_bp as bp

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def home():
    user = current_user
    wordlists = WordList.query.filter_by(user_id=user.id).all()
    results = (
        QuizResult.query.filter_by(user_id=user.id)
        .order_by(QuizResult.date.desc())
        .limit(25)
        .all()
    )

    return render_template(
        "dashboard.html",
        username=user.username,
        wordlists=wordlists,
        results=results,
    )


@dashboard_bp.route("/profile")
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
