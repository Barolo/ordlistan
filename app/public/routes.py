import random
from flask import Blueprint, render_template, flash, url_for, redirect, current_app
from itsdangerous import URLSafeTimedSerializer

from app.models import Word
from app.public import public_bp

public_bp = Blueprint("public", __name__)


# Landing
@public_bp.route("/")
def landing():
    return render_template("landing.html")


# Template filter
@public_bp.app_template_filter("short_label")
def short_label(text, length=28):
    if not text:
        return ""
    return text if len(text) <= length else text[:length-3] + "..."


def get_serializer():
    return URLSafeTimedSerializer(current_app.secret_key)


# Public quiz levels
@public_bp.route("/practice")
def practice():
    return redirect(url_for("public.landing"))


@public_bp.route("/practice/<level>")
def practice_level(level):
    LEVEL_MAP = {
        "easy": {"id": 9001, "label": "Lätt"},
        "medium": {"id": 9002, "label": "Medel"},
        "hard": {"id": 9003, "label": "Svår"},
    }

    key = level.lower()
    if key not in LEVEL_MAP:
        flash("Ogiltig nivå.", "error")
        return redirect(url_for("public.landing"))

    list_id = LEVEL_MAP[key]["id"]
    label = LEVEL_MAP[key]["label"]

    words = Word.query.filter_by(list_id=list_id).all()
    if not words:
        flash("Inga ord i denna nivå.", "error")
        return redirect(url_for("public.landing"))

    groups = {}
    for w in words:
        swe = (w.original or "").strip()
        eng = (w.translation or "").strip()
        if swe and eng:
            groups.setdefault(swe, set()).add(eng)

    unique_questions = list(groups.keys())
    chosen = random.sample(unique_questions, min(11, len(unique_questions)))

    def clean(x):
        return (
            x.lower()
            .replace("!", "").replace("?", "")
            .replace("¡", "").replace("¿", "")
            .replace(".", "").replace(",", "")
            .strip()
        )

    quiz_data = []
    for idx, swe in enumerate(chosen, start=1):
        eng_list = list(groups[swe])
        quiz_data.append({
            "id": idx,
            "question": swe,
            "answers": [clean(e) for e in eng_list],
            "answers_display": ", ".join(eng_list),
        })

    return render_template(
        "practice_level.html",
        level=key,
        level_label=label,
        total_questions=len(quiz_data),
        quiz_data=quiz_data,
    )
