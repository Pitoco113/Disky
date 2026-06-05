#!/usr/bin/env python
"""
Disky - Organizador inteligente de arquivos
Criado por PITOCO113 🇧🇷
"""

import sys
import os
import time
import traceback
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)


def log_msg(msg: str):
    local = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    log_dir = os.path.join(local, "Disky", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "disky.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {msg}\n")


def log_crash(msg: str):
    local = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    log_dir = os.path.join(local, "Disky", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "disky.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(datetime.now().isoformat() + "\n")
        f.write(msg + "\n")
        f.write(traceback.format_exc() + "\n")


def run_background_service():
    """
    Modo segundo plano REAL.
    Roda sem interface, inicia com Windows e organiza automaticamente.
    Usa watchdog quando possível, mas também faz varredura periódica como garantia.
    """
    from core import db
    from core.organizer import FolderWatcher, organize_folder, HAS_WATCHDOG

    db.init_db()
    db.seed_default_rules()
    db.set_config("auto_organize", "1")

    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    if os.path.isdir(downloads):
        db.add_watched_folder(downloads)

    log_msg(f"Disky background iniciado | watchdog={HAS_WATCHDOG}")

    watcher = None
    try:
        watcher = FolderWatcher(app_ref=None)
        if watcher.start():
            log_msg("watchdog iniciado")
        else:
            log_msg("watchdog não iniciou; usando polling")
    except Exception as e:
        log_msg(f"watchdog erro: {e}")
        watcher = None

    # Loop de segurança: mesmo se o evento do watchdog falhar, organiza a cada 6s.
    while True:
        try:
            if db.get_config("auto_organize", "1") == "1":
                for f in db.get_watched_folders():
                    path = f["path"]
                    if os.path.isdir(path):
                        result = organize_folder(path)
                        if result.get("moved", 0):
                            log_msg(f"polling organizou {result['moved']} arquivo(s) em {path}")
        except Exception as e:
            log_msg(f"polling erro: {e}")
        time.sleep(6)


def main():
    try:
        start_hidden = "--background" in sys.argv or "--hidden" in sys.argv
        if start_hidden:
            run_background_service()
            return

        from core.db import init_db, seed_default_rules
        from ui.app import DiskyApp

        init_db()
        seed_default_rules()

        app = DiskyApp(start_hidden=False)
        app.mainloop()
    except Exception:
        log_crash("CRASH NO DISKY")
        raise


if __name__ == "__main__":
    main()
