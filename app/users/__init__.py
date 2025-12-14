from flask import Blueprint

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/profile",
    template_folder="templates"
)

from . import routes
