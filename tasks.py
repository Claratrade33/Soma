from apscheduler.schedulers.background import BackgroundScheduler
from binance_client import get_client
from strategy import decide_and_execute


scheduler = BackgroundScheduler()
scheduler.start()


def auto_trade(usuario_nome: str):
    client = get_client(usuario_nome)
    decide_and_execute(usuario_nome, client)


def start_auto_mode(usuario_nome: str, interval: int = 60):
    job_id = f"auto-{usuario_nome}"
    scheduler.add_job(auto_trade, "interval", [usuario_nome], seconds=interval, id=job_id, replace_existing=True)


def stop_auto_mode(usuario_nome: str):
    job_id = f"auto-{usuario_nome}"
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)
