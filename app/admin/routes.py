from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Word, User, WordList
from app.admin import admin_bp as bp

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ------------------------------------------------------
# ACCESS CONTROL – endast Rikard får gå in här
# ------------------------------------------------------

def admin_required():
    if not current_user.is_authenticated:
        abort(403)
    if current_user.email != "rikard.nygander@gmail.com":
        abort(403)


# ------------------------------------------------------
# Visa alla ord som INTE är globala
# ------------------------------------------------------

@admin_bp.route("/review")
@login_required
def review_words():
    admin_required()

    # Hämta ord som inte är godkända
    pending = Word.query.filter_by(is_global=False).all()

    return render_template("admin_review.html", pending=pending)


# ------------------------------------------------------
# Godkänn ord
# ------------------------------------------------------

@admin_bp.route("/approve/<int:word_id>")
@login_required
def approve_word(word_id):
    admin_required()

    w = Word.query.get(word_id)
    if not w:
        flash("Ordet hittades inte.", "error")
        return redirect(url_for("admin.review_words"))

    w.is_global = True
    db.session.commit()

    flash(f"Godkände '{w.original} = {w.translation}'.", "success")
    return redirect(url_for("admin.review_words"))


# ------------------------------------------------------
# Neka ord
# ------------------------------------------------------

@admin_bp.route("/reject/<int:word_id>")
@login_required
def reject_word(word_id):
    admin_required()

    w = Word.query.get(word_id)
    if not w:
        flash("Ordet hittades inte.", "error")
        return redirect(url_for("admin.review_words"))

    # Alternativ 1: Ta bort ordet
    db.session.delete(w)
    db.session.commit()

    flash(f"Nekade och tog bort '{w.original} = {w.translation}'.", "success")
    return redirect(url_for("admin.review_words"))


@admin_bp.route("/users")
@login_required
def admin_users():
    admin_required()

    users = User.query.all()
    user_data = []

    for u in users:
        wordlist_count = WordList.query.filter_by(user_id=u.id).count()

        created_attr = getattr(u, "created_at", None)
        created_str = (
            created_attr.strftime("%Y-%m-%d %H:%M") if created_attr else "—"
        )

        user_data.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": created_str,
                "wordlist_count": wordlist_count,
            }
        )

    return render_template("admin_users.html", users=user_data)
