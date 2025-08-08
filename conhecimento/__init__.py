from flask import Blueprint

bp = Blueprint('conhecimento', __name__, url_prefix='/conhecimento')

from . import rotas
