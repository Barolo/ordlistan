from flask import render_template
from flask_login import login_required, current_user

from app.stats import stats_bp
from app.models import QuizResult, WordList, Word


@stats_bp.route("/")
@login_required
def stats_page():
    """Visar statistiksidan (stats.html)."""

    # --- Totaler ---
    total_lists = (
        WordList.query.filter_by(user_id=current_user.id).count()
    )

    total_words = (
        Word.query
        .join(WordList)
        .filter(WordList.user_id == current_user.id)
        .count()
    )

    total_quizzes = (
        QuizResult.query.filter_by(user_id=current_user.id).count()
    )

    # --- Resultat över tid ---
    quiz_results = (
        QuizResult.query
        .filter_by(user_id=current_user.id)
        .order_by(QuizResult.date.asc())
        .all()
    )

    quiz_scores = [r.correct_count for r in quiz_results]
    quiz_labels = [r.date.strftime("%Y-%m-%d") for r in quiz_results]

    # --- Svåraste ord ---
    hardest_words = (
        Word.query
        .join(WordList)
        .filter(WordList.user_id == current_user.id)
        .filter(Word.wrong_count > 0)
        .order_by(Word.wrong_count.desc())
        .limit(10)
        .all()
    )

    streak_info = {
    "current": 0,
    "best": 0
}

    # Rendera template
    return render_template(
        "stats/stats.html",
        total_lists=total_lists,
        total_words=total_words,
        total_quizzes=total_quizzes,
        quiz_scores=quiz_scores,
        quiz_labels=quiz_labels,
        hardest_words=hardest_words,
        user=current_user,   # så du kan använda {{ user.username }} i HTML
        streak_info=streak_info
    )
