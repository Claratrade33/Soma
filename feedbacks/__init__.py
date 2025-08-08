from flask import Blueprint

bp = Blueprint('feedbacks', __name__, url_prefix='/feedbacks')

from . import rotas
