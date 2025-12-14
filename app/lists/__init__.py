from flask import Blueprint

lists_bp = Blueprint("lists", __name__, url_prefix="/lists")

from . import routes
