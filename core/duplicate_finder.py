"""
core/duplicate_finder.py - Scanner de arquivos duplicados
Criado por PITOCO113 🇧🇷
"""

import os
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from . import db


def _hash_file_fast(filepath: str) -> tuple:
    """Calcula hash de um arquivo. Retorna (filepath, hash) ou (filepath, None) se erro."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                buf = f.read(65536)
                if not buf:
                    break
                h.update(buf)
        return (filepath, h.hexdigest())
    except (PermissionError, FileNotFoundError, OSError):
        return (filepath, None)


def scan_folder(folder_path: str, progress_callback=None) -> list:
    """
    Escaneia uma pasta em busca de duplicatas.
    Retorna lista de dicts: { file_hash, filename, filepath, size_bytes, modified_at }

    Estratégia otimizada em 3 passos:
    1. Agrupa só por tamanho (arquivos do mesmo tamanho são candidatos)
    2. Calcula hash SHA-256 EM PARALELO usando ThreadPoolExecutor
    3. Agrupa por hash pra achar duplicatas
    """
    if not os.path.isdir(folder_path):
        return []

    # Passo 1: Agrupa TODOS os arquivos por tamanho
    by_size = defaultdict(list)

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith("$") and d != "System Volume Information"]
        for f in files:
            filepath = os.path.join(root, f)
            try:
                size = os.path.getsize(filepath)
                if size == 0:
                    continue
                by_size[size].append(filepath)
            except (PermissionError, OSError):
                continue

    # Passo 2: Só processa tamanhos que têm 2+ arquivos
    all_duplicates = []
    candidates = []
    for size, filepaths in by_size.items():
        if len(filepaths) >= 2:
            candidates.extend(filepaths)

    # Hashing em PARALELO usando ThreadPoolExecutor
    hashes = defaultdict(list)
    total = len(candidates)

    if candidates:
        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as executor:
            results = executor.map(_hash_file_fast, candidates)
            for filepath, fhash in results:
                if fhash:
                    hashes[fhash].append(filepath)

        processed = 0
        for fhash, fps in hashes.items():
            if len(fps) < 2:
                continue
            for fp in fps:
                all_duplicates.append({
                    "file_hash": fhash,
                    "filename": os.path.basename(fp),
                    "filepath": fp,
                    "size_bytes": os.path.getsize(fp),
                    "modified_at": _get_mtime(fp),
                })
            processed += 1
            if progress_callback:
                progress_callback(processed, total)

    return all_duplicates


def _get_mtime(filepath: str) -> str:
    try:
        ts = os.path.getmtime(filepath)
        return datetime.fromtimestamp(ts).isoformat()
    except OSError:
        return ""


def run_full_scan(folders: list, progress_callback=None) -> int:
    """
    Escaneia múltiplas pastas, salva resultados no banco.
    Retorna scan_id.
    """
    init = db.init_db()

    # Cria registro do scan
    scan_id = db.create_scan(folders)

    all_duplicates = []
    total_mb = 0

    for folder in folders:
        dups = scan_folder(folder, progress_callback)
        all_duplicates.extend(dups)
        for d in dups:
            total_mb += d["size_bytes"]

    total_mb = round(total_mb / (1024 * 1024), 2)

    # Salva duplicatas no banco
    if all_duplicates:
        db.add_duplicates(scan_id, all_duplicates)

    # Finaliza scan
    unique_hashes = set(d["file_hash"] for d in all_duplicates)
    db.finish_scan(scan_id, len(unique_hashes), total_mb)

    return scan_id


def group_duplicates(scan_id: int) -> list:
    """
    Retorna grupos de duplicatas do último scan.
    Cada grupo: { hash, filename, count, total_bytes, paths }
    """
    return db.get_duplicate_groups_from_scan(scan_id)


def delete_duplicate(dup_id: int):
    """Marca uma duplicata como deletada (não apaga arquivo ainda)."""
    db.mark_duplicate_deleted(dup_id)


def delete_duplicate_file(dup_id: int) -> bool:
    """Deleta o arquivo duplicado e marca no banco."""
    conn = db.get_db()
    row = conn.execute("SELECT filepath FROM duplicates WHERE id = ?", (dup_id,)).fetchone()
    conn.close()

    if not row:
        return False

    filepath = row["filepath"]
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        db.mark_duplicate_deleted(dup_id)
        return True
    except (PermissionError, OSError):
        return False