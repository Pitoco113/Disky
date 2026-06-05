"""
core/organizer.py - Organizador automático de Downloads
Criado por PITOCO113 🇧🇷
"""

import os
import shutil
import json
import threading
import time
from datetime import datetime
from pathlib import Path

from . import db

# Tenta importar watchdog
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    # Define classes dummy pra não quebrar o código
    class FileSystemEventHandler:
        def on_created(self, event): pass
        def on_modified(self, event): pass
        @property
        def on(self): return False
        @on.setter
        def on(self, value): pass
    class Observer:
        def start(self): pass
        def stop(self): pass
        def join(self, timeout=None): pass
        def schedule(self, *args, **kwargs): pass


# ─── Sistema de Regras ──────────────────────────────────────────

def get_destination(filename: str, rules: list = None) -> tuple:
    """
    Retorna (destino_nome, caminho_completo) baseado nas regras.
    Ex: get_destination("foto.jpg") -> ("Imagens", "Downloads/Imagens/")
    Retorna (None, None) se não achar regra (cai em "Outros").
    """
    if rules is None:
        rules = db.get_rules()

    ext = os.path.splitext(filename)[1].lower()

    for rule in rules:
        if not rule["active"]:
            continue
        extensions = json.loads(rule["extensions"])
        if ext in extensions:
            return rule["name"], rule["destination"]

    return None, None


def organize_file(filepath: str, dest_name: str, dest_folder: str, base_folder: str) -> str:
    """
    Move um arquivo pra pasta de destino.
    Retorna o caminho completo do novo local.
    """
    if not os.path.exists(filepath):
        return None

    filename = os.path.basename(filepath)
    target_dir = os.path.join(base_folder, dest_folder)
    os.makedirs(target_dir, exist_ok=True)

    # Se já existir um arquivo com o mesmo nome, adiciona número
    target_path = os.path.join(target_dir, filename)
    counter = 1
    while os.path.exists(target_path):
        name, ext = os.path.splitext(filename)
        target_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
        counter += 1

    shutil.move(filepath, target_path)

    # Salva no histórico
    db.add_history(filename, filepath, target_path, dest_name)

    return target_path


def organize_folder(folder_path: str, progress_callback=None) -> dict:
    """
    Organiza uma pasta inteira (modo retroativo).
    Retorna { "moved": N, "errors": N, "details": [...] }
    """
    rules = db.get_rules()
    result = {"moved": 0, "errors": 0, "details": []}

    if not os.path.isdir(folder_path):
        return result

    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    total = len(files)
    for i, f in enumerate(files):
        filepath = os.path.join(folder_path, f)

        # Pula arquivos .ffortress e .lnk
        if filepath.endswith(".ffortress") or filepath.endswith(".lnk"):
            continue

        dest_name, dest_folder = get_destination(f, rules)
        if dest_name is None:
            dest_name, dest_folder = "Outros", "Outros"

        try:
            new_path = organize_file(filepath, dest_name, dest_folder, folder_path)
            if new_path:
                result["moved"] += 1
                result["details"].append({
                    "file": f,
                    "from": filepath,
                    "to": new_path,
                    "rule": dest_name,
                })
        except Exception as e:
            result["errors"] += 1
            result["details"].append({
                "file": f,
                "error": str(e),
            })

        if progress_callback:
            progress_callback(i + 1, total)

    return result


# ─── Monitoramento em Tempo Real ────────────────────────────────

class DiskyHandler(FileSystemEventHandler):
    """Monitora novos arquivos na pasta Downloads."""

    def __init__(self, app_ref=None):
        self.app_ref = app_ref  # referência pro app (pra notificar UI)
        self.on = True
        self._processing = set()
        self._lock = threading.Lock()

    def on_created(self, event):
        if not self.on or event.is_directory:
            return
        self._process_later(event.src_path)

    def on_modified(self, event):
        if not self.on or event.is_directory:
            return
        self._process_later(event.src_path)

    def on_moved(self, event):
        if not self.on or event.is_directory:
            return
        # Navegadores costumam baixar .crdownload/.part e depois renomear para o nome final.
        self._process_later(event.dest_path)

    def _process_later(self, filepath):
        filepath = os.path.abspath(filepath)
        with self._lock:
            if filepath in self._processing:
                return
            self._processing.add(filepath)

        def delayed_process():
            try:
                if self._wait_until_stable(filepath):
                    self._process_file(filepath)
            finally:
                with self._lock:
                    self._processing.discard(filepath)
        threading.Thread(target=delayed_process, daemon=True).start()

    def _wait_until_stable(self, filepath, timeout=30):
        """Espera o download/cópia terminar antes de mover o arquivo."""
        last_size = -1
        stable_count = 0
        start = time.time()
        while time.time() - start < timeout:
            if not os.path.exists(filepath):
                return False
            basename = os.path.basename(filepath).lower()
            if basename.endswith((".tmp", ".part", ".crdownload", ".download")):
                time.sleep(1)
                continue
            try:
                size = os.path.getsize(filepath)
            except OSError:
                time.sleep(1)
                continue
            if size == last_size and size > 0:
                stable_count += 1
                if stable_count >= 2:
                    return True
            else:
                stable_count = 0
                last_size = size
            time.sleep(1)
        return False

    def _process_file(self, filepath):
        auto = db.get_config("auto_organize", "1")
        if auto != "1" or not os.path.isfile(filepath):
            return

        basename = os.path.basename(filepath)
        lower = basename.lower()
        if lower.startswith(".") or lower.endswith((".tmp", ".part", ".crdownload", ".download", ".lnk")):
            return

        rules = db.get_rules()
        dest_names = {r["destination"] for r in rules}
        dest_names.add("Outros")

        base_folder = os.path.dirname(filepath)
        parent_name = os.path.basename(base_folder)
        # Evita loop: se o arquivo já está dentro de Documentos/Imagens/etc., não mexe de novo.
        if parent_name in dest_names:
            return

        dest_name, dest_folder = get_destination(basename, rules)
        if dest_name is None:
            dest_name, dest_folder = "Outros", "Outros"

        try:
            new_path = organize_file(filepath, dest_name, dest_folder, base_folder)
            if new_path and self.app_ref:
                self.app_ref.after(0, lambda: self.app_ref.on_file_organized(basename, dest_name))
        except Exception as e:
            if self.app_ref:
                self.app_ref.after(0, lambda: self.app_ref.on_file_organized(f"Erro: {basename}", str(e)[:30]))


class FolderWatcher:
    """Gerencia o watchdog."""

    def __init__(self, app_ref=None):
        self.observer = None
        self.app_ref = app_ref
        self.running = False

    def start(self):
        if not HAS_WATCHDOG:
            return False

        if self.running:
            return True

        folders = db.get_watched_folders()
        if not folders:
            return False

        self.observer = Observer()
        handler = DiskyHandler(self.app_ref)

        for f in folders:
            path = f["path"]
            if os.path.isdir(path):
                self.observer.schedule(handler, path, recursive=False)

        self.observer.start()
        self.running = True
        return True

    def stop(self):
        if self.observer and self.running:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.running = False

    def restart(self):
        self.stop()
        self.start()