from flask import render_template
from flask_login import login_required, current_user
from . import settings_bp


@settings_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html", user=current_user)
