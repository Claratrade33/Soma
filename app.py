# app.py
from __future__ import annotations

import os
from flask import (
    Flask, render_template, render_template_string,
    request, redirect, url_for, flash
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    current_user, login_required
)

# -----------------------------------------------------------------------------
# App & Login
# -----------------------------------------------------------------------------
app = Flask(__name__)

# chave para sessões/flash; use variável de ambiente se quiser
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

login_manager = LoginManager(app)
login_manager.login_view = "usuarios.login"


# -----------------------------------------------------------------------------
# Usuário em memória (admin fixo)
# -----------------------------------------------------------------------------
class AdminUser(UserMixin):
    def __init__(self):
        self.id = "admin"
        self.username = "admin"
        self.password = "Claraverse2025"  # senha padrão solicitada

    # compat helper
    def get_id(self):  # type: ignore[override]
        return self.id


ADMIN = AdminUser()


@login_manager.user_loader
def load_user(user_id: str):
    if user_id == ADMIN.id:
        return ADMIN
    return None


# -----------------------------------------------------------------------------
# Blueprints
# -----------------------------------------------------------------------------
from flask import Blueprint

bp_usuarios = Blueprint("usuarios", __name__, url_prefix="/usuario")
bp_painel = Blueprint("painel", __name__, url_prefix="/painel")
bp_auto = Blueprint("operacoes_automatico", __name__, url_prefix="/operacoes_automatico")


# ------------------------- USUÁRIOS ------------------------------------------
@bp_usuarios.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: mostra um form simples (ou usa o index)
    POST: autentica admin/Claraverse2025 e redireciona ao painel
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == ADMIN.username and password == ADMIN.password:
            login_user(ADMIN)
            flash("Login efetuado com sucesso.", "success")
            return redirect(url_for("painel.dashboard"))
        flash("Credenciais inválidas.", "danger")

    # form simples quando acessar /usuario/login direto
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}Entrar — ClaraVerse{% endblock %}
        {% block content %}
          <div class="row justify-content-center">
            <div class="col-md-6">
              <h3 class="mb-3">Entrar</h3>
              <form method="post">
                <div class="mb-3">
                  <label class="form-label">Usuário</label>
                  <input name="username" class="form-control" value="admin">
                </div>
                <div class="mb-3">
                  <label class="form-label">Senha</label>
                  <input type="password" name="password" class="form-control" value="Claraverse2025">
                </div>
                <button class="btn btn-primary">Entrar</button>
              </form>
            </div>
          </div>
        {% endblock %}
        """
    )


@bp_usuarios.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("index"))


@bp_usuarios.route("/configurar-api")
@login_required
def configurar_api():
    # página placeholder; usa base.html para manter navbar/estilo
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}Corretora — Configurar API{% endblock %}
        {% block content %}
          <h3 class="mb-3">Configurar API da Corretora</h3>
          <p class="text-muted">Tela de exemplo. Aqui você conecta suas chaves.</p>
          <div class="alert alert-info">
            Em breve: formulário para salvar API Key / Secret (Binance).
          </div>
        {% endblock %}
        """
    )


@bp_usuarios.route("/ordens")
@login_required
def ordens():
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}Ordens{% endblock %}
        {% block content %}
          <h3 class="mb-3">Ordens</h3>
          <p class="text-muted">Lista de ordens executadas aparecerá aqui.</p>
        {% endblock %}
        """
    )


@bp_usuarios.route("/historico")
@login_required
def historico():
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}Histórico{% endblock %}
        {% block content %}
          <h3 class="mb-3">Histórico</h3>
          <p class="text-muted">Seu histórico de operações aparecerá aqui.</p>
        {% endblock %}
        """
    )


# ------------------------- PAINEL (OPERACAO) ---------------------------------
@bp_painel.route("/operacao")
@login_required
def dashboard():
    """
    Renderiza templates/painel/dashboard.html se existir.
    Se não existir, mostra um dashboard simples inline.
    """
    # tenta usar arquivo real se você já subiu (recomendado)
    try:
        return render_template("painel/dashboard.html")
    except Exception:
        # fallback simples
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}Dashboard — Operações{% endblock %}
            {% block content %}
              <h2 class="mb-3">Dashboard</h2>
              <div class="row g-3 mb-4">
                <div class="col-md-4"><div class="card p-3 h-100"><h6 class="text-muted">Saldo</h6><div class="display-6">0 <small class="text-muted">USDT</small></div></div></div>
                <div class="col-md-4"><div class="card p-3 h-100"><h6 class="text-muted">Lucro (24h)</h6><div class="display-6">0 <small class="text-muted">USDT</small></div></div></div>
                <div class="col-md-4"><div class="card p-3 h-100"><h6 class="text-muted">Operações Abertas</h6><div class="display-6">0</div></div></div>
              </div>
              <div class="alert alert-info">Suba o arquivo <code>templates/painel/dashboard.html</code> para ver a versão completa.</div>
            {% endblock %}
            """
        )


# ------------------------- AUTOMÁTICO ----------------------------------------
@bp_auto.route("/painel")
@login_required
def painel():
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}Operações Automáticas{% endblock %}
        {% block content %}
          <h3 class="mb-3">Painel — Automático</h3>
          <p class="text-muted">Aqui ficará o controle das estratégias automáticas.</p>
        {% endblock %}
        """
    )


# -----------------------------------------------------------------------------
# Rotas principais
# -----------------------------------------------------------------------------
@app.get("/")
def index():
    # página inicial usa templates/index.html (que te passei)
    return render_template("index.html")


@app.get("/healthz")
def healthz():
    return {"ok": True}


# -----------------------------------------------------------------------------
# Registro dos blueprints
# -----------------------------------------------------------------------------
app.register_blueprint(bp_usuarios)
app.register_blueprint(bp_painel)
app.register_blueprint(bp_auto)


# -----------------------------------------------------------------------------
# Execução local
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # para rodar local: python app.py
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)