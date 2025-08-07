from flask import render_template
from . import bp


@bp.route('/')
def analise():
    return render_template('inteligencia_financeira/analise.html')
