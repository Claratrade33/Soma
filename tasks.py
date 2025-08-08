try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ModuleNotFoundError:  # pragma: no cover - fallback when APScheduler missing
    BackgroundScheduler = None

from binance_client import get_client
from strategy import decide_and_execute


if BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.start()
else:  # simple placeholder to avoid runtime errors when APScheduler isn't installed
    scheduler = None


def auto_trade(usuario_nome: str):
    client = get_client(usuario_nome)
    decide_and_execute(usuario_nome, client)


def start_auto_mode(usuario_nome: str, interval: int = 60):
    if scheduler is None:
        raise RuntimeError("APScheduler não instalado")
    job_id = f"auto-{usuario_nome}"
    scheduler.add_job(auto_trade, "interval", [usuario_nome], seconds=interval, id=job_id, replace_existing=True)


def stop_auto_mode(usuario_nome: str):
    if scheduler is None:
        raise RuntimeError("APScheduler não instalado")
    job_id = f"auto-{usuario_nome}"
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)
