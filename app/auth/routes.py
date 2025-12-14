from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from . import auth_bp
from app import db
from app.extensions import db, mail
from app.models import User
from app.auth import auth_bp as bp

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_serializer():
    return URLSafeTimedSerializer(current_app.secret_key)


# REGISTER
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if not username or not email:
            flash("Alla fält måste fyllas i.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Användarnamnet är upptaget.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("E-post redan registrerad.", "error")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registrering lyckades!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["email_or_username"].strip()
        password = request.form["password"]

        user = User.find_by_identifier(identifier)

        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for("dashboard.home"))

        flash("Fel användarnamn/e-post eller lösenord.", "error")

    return render_template("auth/login.html")


# LOGOUT
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.landing"))


# FORGOT PASSWORD
@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip()
        user = User.query.filter_by(email=email).first()

        if user:
            s = get_serializer()
            token = s.dumps(email, salt="password-reset-salt")
            link = url_for("auth.reset_with_token", token=token, _external=True)

            msg = Message(
                "Återställ lösenord",
                sender=current_app.config.get("MAIL_USERNAME"),
                recipients=[email],
            )
            msg.body = f"Klicka här för att återställa ditt lösenord:\n\n{link}"

            try:
                mail.send(msg)
                flash("Återställningslänk skickad!", "success")
            except:
                flash("Kunde inte skicka e-post.", "error")
        else:
            flash("Ingen användare med den e-posten.", "error")

    return render_template("auth/forgot_password.html")


# RESET PASSWORD
@auth_bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    s = get_serializer()

    try:
        email = s.loads(token, salt="password-reset-salt", max_age=1800)
    except Exception:
        flash("Länken är ogiltig eller har gått ut.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form["new_password"]
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Ingen användare kopplad till denna e-post.", "error")
            return redirect(url_for("auth.forgot_password"))

        user.set_password(new_password)
        db.session.commit()

        flash("Lösenord uppdaterat!", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_with_token.html", token=token)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Kontrollera gammalt lösenord
        if not check_password_hash(current_user.password, old_password):
            flash("Fel nuvarande lösenord.", "danger")
            return redirect(url_for("auth.change_password"))

        # Kontrollera ny match
        if new_password != confirm_password:
            flash("Nya lösenorden matchar inte.", "warning")
            return redirect(url_for("auth.change_password"))

        # Uppdatera lösenord
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Lösenordet har uppdaterats!", "success")
        return redirect(url_for("settings.settings"))

    return render_template("change_password.html")