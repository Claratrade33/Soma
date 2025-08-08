from flask import Blueprint

bp = Blueprint('guardian', __name__, url_prefix='/guardian')

from . import rotas
