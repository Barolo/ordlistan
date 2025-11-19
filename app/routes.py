from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import math
import random
import json

from .extensions import db, mail
from .models import User, WordList, Word, QuizResult
from flask_mail import Message

bp = Blueprint('main', __name__)

# --- Filter för att korta ner listnamn ---
@bp.app_template_filter("short_label")
def short_label(text, length=22):
    if not text:
        return ""
    # Om texten är kortare än limit, returnera som vanligt
    if len(text) <= length:
        return text
    # Annars kapa och lägg till "..."
    return text[:length - 3] + "..."

def get_serializer():
    """Returnerar serializer dynamiskt via current_app."""
    return URLSafeTimedSerializer(current_app.secret_key)

# ------------------- AUTH ROUTES -------------------

# Registrering
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('E-post redan registrerad.', 'error')
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registrering lyckades! Logga in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


# Login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']

        user = User.query.filter(
            (User.email == email_or_username) |
            (User.username == email_or_username)
        ).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('main.home'))

        flash('Fel användarnamn/email eller lösenord.', 'error')

    return render_template('login.html')


# Logout
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du har loggats ut.', 'success')
    return redirect(url_for('main.login'))


# Glömt lösenord
@bp.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            s = get_serializer()
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('main.reset_with_token', token=token, _external=True)
            msg = Message('Återställ lösenord', sender=current_app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'Klicka på länken för att återställa ditt lösenord: {link}'
            mail.send(msg)
            flash('Återställningslänk skickad till din e-post.', 'success')
        else:
            flash('E-post inte registrerad.', 'error')
    return render_template('forgot_password.html')


# Återställ lösenord med token
@bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    s = get_serializer()
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=1800)
    except:
        flash('Länken är ogiltig eller har gått ut.', 'error')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        user = User.query.filter_by(email=email).first()
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Lösenord uppdaterat! Logga in igen.', 'success')
        return redirect(url_for('main.login'))

    return render_template('reset_with_token.html', token=token)


# ------------------- DASHBOARD -------------------
@bp.route('/')
@login_required
def home():
    user = current_user
    wordlists = WordList.query.filter_by(user_id=user.id).all()
    results = QuizResult.query.filter_by(user_id=user.id).order_by(QuizResult.date.desc()).limit(25).all()
    return render_template('dashboard.html', username=user.username, wordlists=wordlists, results=results)


# ------------------- WORDLIST ROUTES -------------------
@bp.route('/create_list', methods=['GET', 'POST'])
@login_required
def create_list():
    if request.method == 'POST':
        list_name = request.form['list_name'].strip()
        if list_name:
            existing = WordList.query.filter_by(name=list_name, user_id=current_user.id).first()
            if existing:
                flash('Du har redan en lista med det namnet.', 'error')
                return redirect(url_for('main.create_list'))
            new_list = WordList(name=list_name, user_id=current_user.id)
            db.session.add(new_list)
            db.session.commit()
            flash('Ordlistan skapades!', 'success')
            return redirect(url_for('main.view_lists'))
        flash('Ange ett namn för listan.', 'error')
    return render_template('create_list.html')


@bp.route('/lists')
@login_required
def view_lists():
    lists = WordList.query.filter_by(user_id=current_user.id).all()
    if not lists:
        flash('Du har inga ordlistor ännu. Skapa en ny!', 'info')
    return render_template('view_lists.html', lists=lists)


@bp.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def view_list(list_id):
    wordlist = WordList.query.filter_by(id=list_id, user_id=current_user.id).first()
    if not wordlist:
        flash("Den här ordlistan finns inte eller tillhör inte dig.", 'error')
        return redirect(url_for('main.view_lists'))

    if request.method == 'POST':
        original = request.form['original'].strip()
        translation = request.form['translation'].strip()
        if original and translation:
            new_word = Word(original=original, translation=translation, list_id=wordlist.id)
            db.session.add(new_word)
            db.session.commit()
            flash("Ordet har lagts till!", "success")
        else:
            flash("Båda fälten måste fyllas i.", "error")
        return redirect(url_for('main.view_list', list_id=list_id))

    return render_template('view_list.html', wordlist=wordlist)

@bp.route('/edit_list/<int:list_id>', methods=['GET','POST'])
@login_required
def edit_list(list_id):
    wordlist = WordList.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not wordlist:
        flash("Ordlistan finns inte eller tillhör inte dig.", "error")
        return redirect(url_for('main.view_lists'))

    if request.method == 'POST':
        new_name = request.form['list_name'].strip()
        if not new_name:
            flash("Ange ett giltigt namn.", "error")
            return redirect(url_for('main.edit_list', list_id=list_id))

        wordlist.name = new_name
        db.session.commit()
        flash("Ordlistans namn har uppdaterats!", "success")
        return redirect(url_for('main.view_lists'))

    return render_template('edit_list.html', wordlist=wordlist)

@bp.route('/edit_word/<int:word_id>/<int:list_id>', methods=['GET', 'POST'])
@login_required
def edit_word(word_id, list_id):
    word = Word.query.join(WordList).filter(
        Word.id == word_id,
        WordList.user_id == current_user.id
    ).first()

    if not word:
        flash("Ordet finns inte eller tillhör inte dig.", "error")
        return redirect(url_for('main.view_list', list_id=list_id))

    if request.method == 'POST':
        original = request.form['original'].strip()
        translation = request.form['translation'].strip()

        if original and translation:
            word.original = original
            word.translation = translation
            db.session.commit()
            flash("Ordet uppdaterades!", "success")
            return redirect(url_for('main.view_list', list_id=list_id))
        else:
            flash("Fyll i både original och översättning.", "error")

    return render_template('edit_word.html', word=word, list_id=list_id)


@bp.route('/delete_list/<int:list_id>', methods=['POST'])
@login_required
def delete_list(list_id):
    wordlist = WordList.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not wordlist:
        flash("Ordlistan finns inte eller tillhör inte dig.", "error")
        return redirect(url_for('main.view_lists'))

    db.session.delete(wordlist)
    db.session.commit()
    
    flash("Ordlistan har tagits bort.", "success")
    return redirect(url_for('main.view_lists'))

@bp.route('/delete_word/<int:word_id>/<int:list_id>', methods=['POST'])
@login_required
def delete_word(word_id, list_id):
    word = Word.query.join(WordList).filter(
        Word.id == word_id,
        WordList.user_id == current_user.id
    ).first()

    if not word:
        flash("Ordet finns inte eller tillhör inte dig.", "error")
        return redirect(url_for('main.view_list', list_id=list_id))

    db.session.delete(word)
    db.session.commit()
    flash("Ordet har tagits bort.", "success")

    return redirect(url_for('main.view_list', list_id=list_id))


# ------------------- QUIZ ROUTES -------------------
@bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz_settings():

    # sortera på senast skapad överst
    wordlists = WordList.query.filter_by(user_id=current_user.id) \
                            .order_by(WordList.created_at.desc()) \
                            .all()

    if request.method == 'POST':
        selected_lists = request.form.getlist('lists')
        num_questions = request.form.get('num_words', type=int)
        direction = request.form.get('direction', 'mix')

        # Hantera "alla listor"
        if "all" in selected_lists:
            lists_str = "all"
        else:
            lists_str = ",".join(selected_lists)

        return redirect(url_for(
            'main.quiz_take',
            lists=lists_str,
            num_words=num_questions,
            direction=direction
        ))

    return render_template('quiz_settings.html', wordlists=wordlists)


@bp.route('/quiz/take')
@login_required
def quiz_take():

    lists_param = request.args.get('lists', '')
    num_words = request.args.get('num_words', type=int, default=5)
    direction = request.args.get('direction', 'mix')

    # ---- HÄMTA RÄTTA ORD ----
    if lists_param == "all":
        words = Word.query.join(WordList).filter(WordList.user_id == current_user.id).all()
    else:
        list_ids = [int(x) for x in lists_param.split(',') if x.isdigit()]
        words = Word.query.filter(Word.list_id.in_(list_ids)).all()

    if not words:
        flash("Inga ord i de valda listorna.", "error")
        return redirect(url_for('main.quiz_settings'))

    # ---- VIKTNING ----
    weighted = []
    weights = []

    for w in words:
        wrong = w.wrong_count or 0
        correct = w.correct_count or 0
        diff = wrong - correct
        weight = 1 if diff <= 0 else 1 + math.log(1 + diff)

        weighted.append(w)
        weights.append(weight)

    # ---- SLUMP MED UPPREPNING ----
    selected = random.choices(weighted, weights=weights, k=num_words)

    # ---- FUNKTION FÖR ATT RENGÖRA SVAR ----
    def clean(s: str) -> str:
        return s.lower().replace("!", "").replace("?", "").replace("¡", "").replace("¿", "").replace(".", "").replace(",", "").strip()

    # ---- BYGG quiz_data ----
    quiz_data = []

    for w in selected:

        # Basord (eng → sv enligt dina data)
        eng = w.original.strip()
        swe = w.translation.strip()

        # Alla acceptabla svar: eftersom samma eng-ord kan finnas i flera listor
        all_translations = Word.query.filter(
            Word.original == w.original,
            Word.list_id.in_(list_ids if lists_param != "all" else
                            [wl.id for wl in WordList.query.filter_by(user_id=current_user.id).all()])
        ).all()

        # Sanera alla möjligheter
        all_answer_forms_translation = list({clean(x.translation) for x in all_translations})
        all_answer_forms_original = list({clean(x.original) for x in all_translations})

        # Kontrollera riktning
        if direction == "sv_en":
            question = swe
            answers = all_answer_forms_original
        elif direction == "en_sv":
            question = eng
            answers = all_answer_forms_translation
        else:  # MIX
            if random.random() < 0.5:
                question = swe
                answers = all_answer_forms_original
            else:
                question = eng
                answers = all_answer_forms_translation

        quiz_data.append({
            "id": w.id,                                # behövs för statistiken
            "question": question,
            "answers": answers,
            "wrong_count": w.wrong_count or 0,         # behövs för viktning i JS
            "correct_count": w.correct_count or 0
        })

    return render_template("quiz_take.html", quiz_data=quiz_data)


@bp.route("/quiz/finish", methods=["POST"])
@login_required
def quiz_finish():
    user = current_user

    correct = int(request.form.get("correct", 0))
    total = int(request.form.get("total", 0))

    # Spara quizresultat
    result = QuizResult(user_id=user.id, correct_count=correct, total_questions=total)
    db.session.add(result)
    db.session.commit()

    # Uppdatera ordstatistik
    answers = request.form.get("answers")
    if answers:
        answers = json.loads(answers)
        for a in answers:
            word = Word.query.get(a['id'])
            if word:
                if a['correct']:
                    word.correct_count += 1
                else:
                    word.wrong_count += 1
                    word.last_wrong = datetime.utcnow()
        db.session.commit()

    # --- Hämta uppdaterad statistik ---
    wordlists = WordList.query.filter_by(user_id=user.id).all()
    total_words = sum(len(wl.words) for wl in wordlists)
    total_lists = len(wordlists)
    total_quizzes = QuizResult.query.filter_by(user_id=user.id).count()

    # Svåraste ord
    hardest_words = []
    for wl in wordlists:
        for w in wl.words:
            hardest_words.append({
                "original": w.original,
                "wrong_count": getattr(w, "wrong_count", 0),
                "correct_count": getattr(w, "correct_count", 0),
                "last_wrong": w.last_wrong.strftime("%d %b") if getattr(w, "last_wrong", None) else "–"
            })

    hardest_words.sort(key=lambda x: x['wrong_count'], reverse=True)

    # --- Skicka tillbaka all statistik ---
    return jsonify({
        "status": "ok",
        "correct": correct,
        "total": total,
        "total_words": total_words,
        "total_lists": total_lists,
        "total_quizzes": total_quizzes,
        "hardest_words": hardest_words
    })


# ------------------- PROFILE -------------------
@bp.route("/profile")
@login_required
def profile():
    user = current_user
    wordlists = WordList.query.filter_by(user_id=user.id).all()
    total_words = sum(len(wl.words) for wl in wordlists)
    total_lists = len(wordlists)

    quizzes = QuizResult.query.filter_by(user_id=user.id).order_by(QuizResult.date).all()
    total_quizzes = len(quizzes)
    quiz_labels = [q.date.strftime("%d %b") for q in quizzes]
    quiz_scores = [q.correct_count for q in quizzes]

    hardest_words = []
    for wl in wordlists:
        for w in wl.words:
            hardest_words.append({
                "original": w.original,
                "wrong_count": getattr(w, "wrong_count", 0),
                "correct_count": getattr(w, "correct_count", 0),
                "last_wrong": w.last_wrong.strftime("%d %b") if getattr(w, "last_wrong", None) else "–"
            })

    hardest_words.sort(key=lambda x: x['wrong_count'], reverse=True)

    return render_template(
        "profile.html",
        user=user,
        total_words=total_words,
        total_lists=total_lists,
        total_quizzes=total_quizzes,
        quiz_labels=quiz_labels,
        quiz_scores=quiz_scores,
        hardest_words=hardest_words
    )
