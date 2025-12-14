from datetime import datetime
import math
import random
import json

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Word, WordList, QuizResult, QuizAnswerLog

# SKAPA BLUEPRINTEN (den enda!)
quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")


# ------------------------------------------------------
# QUIZ SETTINGS
# ------------------------------------------------------

@quiz_bp.route("/", methods=["GET", "POST"])
@login_required
def quiz_settings():
    """Inställningar: välj listor, riktning, antal ord."""
    wordlists = (
        WordList.query.filter_by(user_id=current_user.id)
        .order_by(WordList.id.desc())
        .all()
    )

    if request.method == "POST":
        selected_lists = request.form.getlist("lists")
        num_questions = request.form.get("num_words", type=int)
        direction = request.form.get("direction", "mix")

        if "all" in selected_lists:
            lists_str = "all"
        else:
            lists_str = ",".join(selected_lists)

        return redirect(
            url_for(
                "quiz.quiz_take",
                lists=lists_str,
                num_words=num_questions,
                direction=direction,
            )
        )

    return render_template("quiz_settings.html", wordlists=wordlists)


# ------------------------------------------------------
# QUIZ GENERATION
# ------------------------------------------------------

@quiz_bp.route("/take")
@login_required
def quiz_take():
    """Genererar frågorna för ett förhör."""
    lists_param = request.args.get("lists", "")
    num_words = request.args.get("num_words", type=int, default=5)
    direction = request.args.get("direction", "mix")

    # Hämta ordlistor
    if lists_param == "all":
        words = (
            Word.query.join(WordList)
            .filter(WordList.user_id == current_user.id)
            .all()
        )
        all_user_list_ids = [
            wl.id for wl in WordList.query.filter_by(user_id=current_user.id).all()
        ]
    else:
        list_ids = [int(x) for x in lists_param.split(",") if x.isdigit()]
        words = Word.query.filter(Word.list_id.in_(list_ids)).all()
        all_user_list_ids = list_ids

    if not words:
        flash("Inga ord i de valda listorna.", "error")
        return redirect(url_for("quiz.quiz_settings"))

    # ------------------------
    # Viktning av ord
    # ------------------------
    weighted = []
    weights = []

    for w in words:
        wrong = w.wrong_count or 0
        correct = w.correct_count or 0
        diff = wrong - correct

        weight = 1 if diff <= 0 else 1 + math.log(1 + diff)

        weighted.append(w)
        weights.append(weight)

    selected = random.choices(weighted, weights=weights, k=num_words)

    def clean(s: str) -> str:
        return (
            s.lower()
            .replace("!", "")
            .replace("?", "")
            .replace("¡", "")
            .replace("¿", "")
            .replace(".", "")
            .replace(",", "")
            .strip()
        )

    quiz_data = []

    for w in selected:
        eng = w.original.strip()
        swe = w.translation.strip()

        # Hämta alla alternativa svar
        all_translations = Word.query.filter(
            Word.original == w.original,
            Word.list_id.in_(all_user_list_ids),
        ).all()

        all_answer_forms_translation = list({clean(x.translation) for x in all_translations})
        all_answer_forms_original = list({clean(x.original) for x in all_translations})

        # Vilket håll frågan ska gå
        if direction == "sv_en":
            question = swe
            answers = all_answer_forms_original
        elif direction == "en_sv":
            question = eng
            answers = all_answer_forms_translation
        else:
            if random.random() < 0.5:
                question = swe
                answers = all_answer_forms_original
            else:
                question = eng
                answers = all_answer_forms_translation

        quiz_data.append(
            {
                "id": w.id,
                "question": question,
                "answers": answers,
                "wrong_count": w.wrong_count or 0,
                "correct_count": w.correct_count or 0,
            }
        )

    return render_template("quiz_take.html", quiz_data=quiz_data)

@quiz_bp.route("/quick/<int:list_id>")
@login_required
def quick_quiz(list_id):
    wordlist = WordList.query.get_or_404(list_id)

    # kontroll: listan måste tillhöra användaren
    if wordlist.user_id != current_user.id:
        abort(403)

    words = wordlist.words  # SQLAlchemy relationship

    # hur många frågor ska genereras
    QUIZ_SIZE = 11

    if len(words) == 0:
        flash("Listan innehåller inga ord.", "error")
        return redirect(url_for("lists.view_all"))

    if len(words) >= QUIZ_SIZE:
        # 11 helt unika slumpade ord
        selected = random.sample(words, QUIZ_SIZE)
    else:
        # färre än 11 ord → repetition tillåten
        selected = [random.choice(words) for _ in range(QUIZ_SIZE)]

    # spara ordens IDs i sessionen för quizet
    session["quick_quiz_words"] = [w.id for w in selected]
    session["quiz_list_name"] = wordlist.name

    return redirect(url_for("quiz.run_quick_quiz"))

@quiz_bp.route("/quick/run")
@login_required
def run_quick_quiz():
    ids = session.get("quick_quiz_words")
    if not ids:
        flash("Inget snabbförhör skapat.", "error")
        return redirect(url_for("dashboard.home"))

    words = Word.query.filter(Word.id.in_(ids)).all()

    return render_template("quiz/quick_quiz.html", words=words, list_name=session.get("quiz_list_name"))


# ------------------------------------------------------
# FINISH QUIZ
# ------------------------------------------------------

@quiz_bp.route("/finish", methods=["POST"])
@login_required
def quiz_finish():
    """Tar emot resultat, uppdaterar DB (resultat + answer-loggar + ordstatistik) och skickar statistik tillbaka."""
    user = current_user

    correct = int(request.form.get("correct", 0))
    total = int(request.form.get("total", 0))

    # 1) Skapa quiz-resultat
    result = QuizResult(
        user_id=user.id,
        correct_count=correct,
        total_questions=total,
    )
    db.session.add(result)
    db.session.flush()  # så vi får ett id direkt utan att committa än

    # 2) Spara per-fråga-logg + uppdatera ord-statistik
    answers = request.form.get("answers")
    if answers:
        answer_list = json.loads(answers)

        for a in answer_list:
            word_id = a.get("id")
            is_correct = bool(a.get("correct"))
            user_answer = a.get("user_answer", "")

            # Hämta ordet
            word = Word.query.get(word_id)
            if not word:
                continue  # defensivt, om något konstigt skulle ske

            # Uppdatera word-statistik (cache för snabbare viktning)
            if is_correct:
                word.correct_count = (word.correct_count or 0) + 1
            else:
                word.wrong_count = (word.wrong_count or 0) + 1
                word.last_wrong = datetime.utcnow()

            # Logga svaret i quiz_answer_log
            log = QuizAnswerLog(
                user_id=user.id,
                quiz_result_id=result.id,
                word_id=word.id,
                user_answer=user_answer,
                is_correct=is_correct,
            )
            db.session.add(log)

    # 3) Commita allt i ett svep
    db.session.commit()

    # 4) Sammanställ lite övergripande statistik till frontend
    wordlists = WordList.query.filter_by(user_id=user.id).all()
    total_words = sum(len(wl.words) for wl in wordlists)
    total_lists = len(wordlists)
    total_quizzes = QuizResult.query.filter_by(user_id=user.id).count()

    # Hårdkodad “hardest words”-lista för nu (kan bytas till att bygga på QuizAnswerLog senare)
    from app.services.analytics import get_hardest_words

    hardest_words = get_hardest_words(user.id)

    return jsonify(
        {
            "status": "ok",
            "correct": correct,
            "total": total,
            "total_words": total_words,
            "total_lists": total_lists,
            "total_quizzes": total_quizzes,
            "hardest_words": hardest_words,
        }
    )
