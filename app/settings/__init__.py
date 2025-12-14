from flask import Blueprint

settings_bp = Blueprint(
    "settings",
    __name__,
    template_folder="templates",
    static_folder="static"
)

from . import routes
