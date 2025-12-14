from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import WordList, Word

lists_bp = Blueprint('lists', __name__, url_prefix="/lists")

# ---------------------------------------------
# VIEW ALL LISTS
# ---------------------------------------------
@lists_bp.route("/")
@login_required
def view_all():
    lists = WordList.query.filter_by(user_id=current_user.id).all()
    return render_template("lists/view_all.html", lists=lists)

# ---------------------------------------------
# CREATE LIST
# ---------------------------------------------
@lists_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_list():
    if request.method == "POST":
        name = request.form.get("list_name")

        if not name or len(name) < 2:
            flash("Listnamnet är för kort.", "error")
            return redirect(url_for("lists.create_list"))

        wl = WordList(name=name, user_id=current_user.id)
        db.session.add(wl)
        db.session.commit()

        flash("Ordlista skapad!", "success")
        return redirect(url_for("lists.view_list", list_id=wl.id))

    return render_template("lists/create_list.html")

# ---------------------------------------------
# VIEW SINGLE LIST
# ---------------------------------------------
@lists_bp.route("/<int:list_id>")
@login_required
def view_list(list_id):
    wl = WordList.query.get_or_404(list_id)
    if wl.user_id != current_user.id:
        return redirect(url_for("lists.view_all"))

    words = Word.query.filter_by(list_id=wl.id).all()
    return render_template("lists/view_list.html", wordlist=wl, words=words)

# ---------------------------------------------
# EDIT LIST NAME (GET + POST)
# ---------------------------------------------
@lists_bp.route("/<int:list_id>/edit", methods=["GET", "POST"])
@login_required
def edit_list(list_id):
    wl = WordList.query.get_or_404(list_id)

    if wl.user_id != current_user.id:
        return redirect(url_for("lists.view_all"))

    if request.method == "POST":
        new_name = request.form.get("list_name")
        if new_name and len(new_name) >= 2:
            wl.name = new_name
            db.session.commit()
            flash("Listnamnet har uppdaterats!", "success")
            return redirect(url_for("lists.view_list", list_id=list_id))
        else:
            flash("Listnamnet är för kort.", "error")

    return render_template("lists/edit_list.html", wordlist=wl)

# ---------------------------------------------
# DELETE LIST
# ---------------------------------------------
@lists_bp.route("/<int:list_id>/delete", methods=["POST"])
@login_required
def delete_list(list_id):
    wl = WordList.query.get_or_404(list_id)

    if wl.user_id != current_user.id:
        return redirect(url_for("lists.view_all"))

    db.session.delete(wl)
    db.session.commit()
    flash("Ordlista borttagen.", "success")

    return redirect(url_for("lists.view_all"))

# ---------------------------------------------
# ADD WORD
# ---------------------------------------------
@lists_bp.route("/<int:list_id>/add", methods=["POST"])
@login_required
def add_word(list_id):
    wl = WordList.query.get_or_404(list_id)

    if wl.user_id != current_user.id:
        return redirect(url_for("lists.view_all"))

    original = request.form.get("original")
    translation = request.form.get("translation")

    if not original or not translation:
        flash("Båda fälten måste fyllas i.", "error")
        return redirect(url_for("lists.view_list", list_id=list_id))

    word = Word(original=original, translation=translation, list_id=wl.id)
    db.session.add(word)
    db.session.commit()

    flash("Ord tillagt!", "success")

    return redirect(url_for("lists.view_list", list_id=list_id))

# ---------------------------------------------
# EDIT WORD
# ---------------------------------------------
@lists_bp.route("/word/<int:word_id>/edit", methods=["GET", "POST"])
@login_required
def edit_word(word_id):
    w = Word.query.get_or_404(word_id)
    wl = WordList.query.get_or_404(w.list_id)

    if wl.user_id != current_user.id:
        return redirect(url_for("lists.view_all"))

    if request.method == "POST":
        w.original = request.form.get("original")
        w.translation = request.form.get("translation")
        db.session.commit()
        flash("Ordet uppdaterades!", "success")
        return redirect(url_for("lists.view_list", list_id=wl.id))

    return render_template("lists/edit_word.html", word=w)

# ---------------------------------------------
# DELETE WORD
# ---------------------------------------------
@lists_bp.route("/word/<int:word_id>/delete")
@login_required
def delete_word(word_id):
    w = Word.query.get_or_404(word_id)

    wl = WordList.query.get_or_404(w.list_id)
    if wl.user_id != current_user.id:
        return redirect(url_for("lists.view_all"))

    db.session.delete(w)
    db.session.commit()

    flash("Ord borttaget.", "success")
    return redirect(url_for("lists.view_list", list_id=wl.id))
