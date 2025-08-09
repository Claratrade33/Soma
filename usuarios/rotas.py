import os, base64, json
from flask import Blueprint, render_template, request, redirect, url_for, flash

bp_api = Blueprint("usuario_api", __name__, url_prefix="/usuario")

SAFE_DIR = "tokens"
SAFE_FILE = os.path.join(SAFE_DIR, "apis.json")

os.makedirs(SAFE_DIR, exist_ok=True)
if not os.path.exists(SAFE_FILE):
    with open(SAFE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def _save_user_keys(user_id, exchange, api_key, api_secret):
    with open(SAFE_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[user_id] = data.get(user_id, {})
        data[user_id][exchange] = {
            "api_key": base64.b64encode(api_key.encode()).decode(),
            "api_secret": base64.b64encode(api_secret.encode()).decode(),
        }
        f.seek(0); json.dump(data, f, ensure_ascii=False, indent=2); f.truncate()

def _get_user_keys(user_id, exchange):
    if not os.path.exists(SAFE_FILE): return None
    with open(SAFE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        rec = data[user_id][exchange]
        return {
            "api_key": base64.b64decode(rec["api_key"]).decode(),
            "api_secret": base64.b64decode(rec["api_secret"]).decode(),
        }
    except Exception:
        return None

@bp_api.route("/configurar-api", methods=["GET", "POST"])
def configurar_api():
    # Em produção, use o ID real do usuário autenticado
    user_id = "demo-user"

    if request.method == "POST":
        exchange = request.form.get("exchange", "binance")
        api_key = request.form.get("api_key", "").strip()
        api_secret = request.form.get("api_secret", "").strip()
        if not api_key or not api_secret:
            flash("Preencha API Key e Secret.", "danger")
            return redirect(url_for("usuario_api.configurar_api"))
        _save_user_keys(user_id, exchange, api_key, api_secret)
        flash("Credenciais salvas. Vamos testar…", "success")
        return redirect(url_for("usuario_api.testar_api", exchange=exchange))

    return render_template("usuarios/config_api.html")

@bp_api.route("/testar-api")
def testar_api():
    user_id = "demo-user"
    exchange = request.args.get("exchange", "binance")
    creds = _get_user_keys(user_id, exchange)
    ok = False; erro = None
    if creds:
        # Teste “a seco”. Em produção, chame a API real (ex.: GET /api/v3/account na Binance).
        try:
            ok = bool(creds["api_key"] and creds["api_secret"])
        except Exception as e:
            erro = str(e)
    return render_template("usuarios/teste_api.html", ok=ok, erro=erro, exchange=exchange)