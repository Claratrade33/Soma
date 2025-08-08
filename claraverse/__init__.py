from flask import Blueprint

bp = Blueprint('claraverse', __name__, url_prefix='/claraverse')

from . import rotas
