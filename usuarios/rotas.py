from flask import render_template
from . import bp


@bp.route('/')
def listar():
    return render_template('usuarios/listar_usuarios.html')


@bp.route('/novo')
def novo_usuario():
    return render_template('usuarios/novo_usuario.html')
