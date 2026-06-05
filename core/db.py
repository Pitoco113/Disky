"""
core/db.py - Banco de dados SQLite do Disky
Criado por PITOCO113 🇧🇷

Salva: regras do usuário, histórico de organização, duplicatas encontradas, configs
"""

import sqlite3
import os
import json
import shutil
from datetime import datetime

# Banco persistente de verdade: fica no AppData do usuário, não dentro do .exe/projeto.
# Assim as configurações sobrevivem ao fechar, instalar, atualizar e recompilar.
APPDATA_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local"),
    "Disky",
)
DB_DIR = os.path.join(APPDATA_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "disky.db")

# Caminho antigo usado durante o desenvolvimento. Se existir, migramos uma vez.
OLD_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "disky.db")


def init_db():
    """Cria o banco e as tabelas se não existirem."""
    os.makedirs(DB_DIR, exist_ok=True)

    # Migração automática do banco antigo do projeto para o AppData.
    if not os.path.exists(DB_PATH) and os.path.exists(OLD_DB_PATH):
        try:
            shutil.copy2(OLD_DB_PATH, DB_PATH)
        except Exception:
            pass

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Configurações gerais
    c.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Pastas monitoradas
    c.execute("""
        CREATE TABLE IF NOT EXISTS watched_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            active INTEGER DEFAULT 1,
            added_at TEXT NOT NULL
        )
    """)

    # Regras de organização
    c.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            extensions TEXT NOT NULL,
            destination TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    # Histórico de organização
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            from_path TEXT NOT NULL,
            to_path TEXT NOT NULL,
            rule_name TEXT,
            organized_at TEXT NOT NULL
        )
    """)

    # Escaneamentos de duplicatas
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanned_at TEXT NOT NULL,
            total_duplicates INTEGER DEFAULT 0,
            space_wasted_mb REAL DEFAULT 0,
            folders_scanned TEXT
        )
    """)

    # Duplicatas encontradas
    c.execute("""
        CREATE TABLE IF NOT EXISTS duplicates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            file_hash TEXT,
            filename TEXT,
            filepath TEXT NOT NULL,
            size_bytes INTEGER DEFAULT 0,
            modified_at TEXT,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        )
    """)

    # Wizard completed flag
    c.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('wizard_done', '0')")
    c.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('language', 'pt_BR')")
    c.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('auto_organize', '1')")
    c.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('run_on_startup', '1')")
    c.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('last_scan', '0')")

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Configurações ──────────────────────────────────────────────

def get_config(key: str, default=None):
    conn = get_db()
    row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row:
        return row["value"]
    return default


def set_config(key: str, value: str):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
        (key, str(value)),
    )
    conn.commit()
    conn.close()


# ─── Regras ────────────────────────────────────────────────────

def get_rules():
    conn = get_db()
    rows = conn.execute("SELECT * FROM rules ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_rule(name: str, extensions: list, destination: str):
    conn = get_db()
    conn.execute(
        "INSERT INTO rules (name, extensions, destination, active, created_at) VALUES (?, ?, ?, 1, ?)",
        (name, json.dumps(extensions), destination, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def update_rule(rule_id: int, name: str = None, extensions: list = None,
                destination: str = None, active: int = None):
    conn = get_db()
    fields = []
    values = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if extensions is not None:
        fields.append("extensions = ?")
        values.append(json.dumps(extensions))
    if destination is not None:
        fields.append("destination = ?")
        values.append(destination)
    if active is not None:
        fields.append("active = ?")
        values.append(active)
    values.append(rule_id)
    conn.execute(f"UPDATE rules SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_rule(rule_id: int):
    conn = get_db()
    conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()


def seed_default_rules():
    """Adiciona regras padrão se não existirem."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
    conn.close()
    if count > 0:
        return

    defaults = [
        ("📄 Documentos", [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".odt", ".csv", ".pptx"], "Documentos"),
        ("🖼️ Imagens", [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"], "Imagens"),
        ("🎵 Músicas", [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"], "Músicas"),
        ("🎬 Vídeos", [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm", ".mpeg"], "Vídeos"),
        ("💿 Instaladores", [".exe", ".msi", ".dmg", ".appimage", ".run"], "Instaladores"),
        ("📦 Compactados", [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"], "Compactados"),
        ("📚 E-books", [".epub", ".mobi", ".cbr", ".cbz", ".pdf"], "E-books"),
    ]
    for name, exts, dest in defaults:
        add_rule(name, exts, dest)


# ─── Pastas Monitoradas ─────────────────────────────────────────

def get_watched_folders():
    conn = get_db()
    rows = conn.execute("SELECT * FROM watched_folders WHERE active = 1").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_watched_folder(path: str):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO watched_folders (path, active, added_at) VALUES (?, 1, ?)",
            (path, datetime.now().isoformat()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # já existe
    conn.close()


def remove_watched_folder(folder_id: int):
    conn = get_db()
    conn.execute("DELETE FROM watched_folders WHERE id = ?", (folder_id,))
    conn.commit()
    conn.close()


# ─── Histórico ─────────────────────────────────────────────────

def add_history(filename: str, from_path: str, to_path: str, rule_name: str):
    conn = get_db()
    conn.execute(
        "INSERT INTO history (filename, from_path, to_path, rule_name, organized_at) VALUES (?, ?, ?, ?, ?)",
        (filename, from_path, to_path, rule_name, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_recent_history(limit: int = 20):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY organized_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history_count() -> int:
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    conn.close()
    return count


# ─── Duplicatas ─────────────────────────────────────────────────

def create_scan(folders_scanned: list) -> int:
    conn = get_db()
    c = conn.execute(
        "INSERT INTO scans (scanned_at, folders_scanned) VALUES (?, ?)",
        (datetime.now().isoformat(), json.dumps(folders_scanned)),
    )
    scan_id = c.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def finish_scan(scan_id: int, total: int, space_mb: float):
    conn = get_db()
    conn.execute(
        "UPDATE scans SET total_duplicates = ?, space_wasted_mb = ? WHERE id = ?",
        (total, space_mb, scan_id),
    )
    conn.commit()
    conn.close()
    set_config("last_scan", datetime.now().isoformat())


def add_duplicates(scan_id: int, duplicates: list):
    """duplicates: list of dicts com file_hash, filename, filepath, size_bytes, modified_at"""
    conn = get_db()
    for d in duplicates:
        conn.execute(
            "INSERT INTO duplicates (scan_id, file_hash, filename, filepath, size_bytes, modified_at) VALUES (?, ?, ?, ?, ?, ?)",
            (scan_id, d["file_hash"], d["filename"], d["filepath"], d["size_bytes"], d.get("modified_at", "")),
        )
    conn.commit()
    conn.close()


def get_last_scan() -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM scans ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_duplicates_from_scan(scan_id: int, only_active: bool = True):
    conn = get_db()
    if only_active:
        rows = conn.execute(
            "SELECT * FROM duplicates WHERE scan_id = ? AND is_deleted = 0 ORDER BY size_bytes DESC",
            (scan_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM duplicates WHERE scan_id = ? ORDER BY size_bytes DESC",
            (scan_id,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_duplicate_groups_from_scan(scan_id: int):
    """Agrupa duplicatas por hash. Retorna lista de grupos."""
    conn = get_db()
    rows = conn.execute(
        """SELECT file_hash, filename, COUNT(*) as count, SUM(size_bytes) as total_bytes,
                  GROUP_CONCAT(filepath, '||') as paths
           FROM duplicates
           WHERE scan_id = ? AND is_deleted = 0
           GROUP BY file_hash
           HAVING count > 1
           ORDER BY total_bytes DESC""",
        (scan_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_duplicate_deleted(dup_id: int):
    conn = get_db()
    conn.execute("UPDATE duplicates SET is_deleted = 1 WHERE id = ?", (dup_id,))
    conn.commit()
    conn.close()


# ─── Estatísticas ──────────────────────────────────────────────

def get_stats() -> dict:
    conn = get_db()
    total_organized = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    total_duplicates = conn.execute("SELECT COALESCE(SUM(space_wasted_mb), 0) FROM scans").fetchone()[0]
    total_rules = conn.execute("SELECT COUNT(*) FROM rules WHERE active = 1").fetchone()[0]
    conn.close()
    return {
        "organized": total_organized,
        "space_found_mb": round(total_duplicates, 1),
        "active_rules": total_rules,
    }