"""
core/install.py - Instalação Windows do Disky
Criado por PITOCO113 🇧🇷

Copia o executável para uma pasta de app real no Windows e cria atalhos no Desktop e na Inicialização.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "Disky"
CREATOR = "PITOCO113 🇧🇷"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def app_install_dir() -> str:
    local = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    return os.path.join(local, "Programs", APP_NAME)


def installed_exe_path() -> str:
    return os.path.join(app_install_dir(), "Disky.exe")


def current_executable() -> str:
    """Retorna o .exe real quando empacotado; durante dev tenta dist/Disky.exe."""
    if is_frozen():
        return sys.executable
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dev_exe = os.path.join(root, "dist", "Disky.exe")
    if os.path.exists(dev_exe):
        return dev_exe
    return sys.executable


def icon_path() -> str:
    install_icon = os.path.join(app_install_dir(), "icon.ico")
    if os.path.exists(install_icon):
        return install_icon
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dev_icon = os.path.join(root, "build", "icon.ico")
    return dev_icon if os.path.exists(dev_icon) else installed_exe_path()


def _ps_quote(s: str) -> str:
    return s.replace("'", "''")


def _run_powershell(script: str):
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "PowerShell falhou").strip())
    return result


def get_special_folder(name: str) -> str:
    """Desktop/Startup via WScript, respeitando OneDrive/Desktop redirecionado."""
    ps = f"$ws=New-Object -ComObject WScript.Shell; Write-Output $ws.SpecialFolders.Item('{name}')"
    result = _run_powershell(ps)
    path = result.stdout.strip().splitlines()[-1].strip()
    if not path:
        raise RuntimeError(f"Não consegui localizar a pasta especial: {name}")
    return path


def create_shortcut(shortcut_path: str, target: str, args: str = "", description: str = ""):
    os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
    ico = icon_path()
    workdir = os.path.dirname(target)
    ps = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{_ps_quote(shortcut_path)}')
$s.TargetPath = '{_ps_quote(target)}'
$s.Arguments = '{_ps_quote(args)}'
$s.WorkingDirectory = '{_ps_quote(workdir)}'
$s.Description = '{_ps_quote(description or (APP_NAME + ' - ' + CREATOR))}'
$s.IconLocation = '{_ps_quote(ico)}'
$s.Save()
"""
    _run_powershell(ps)


def install_app(enable_startup: bool = True) -> dict:
    """
    Instala o Disky como app normal do Windows:
    - copia Disky.exe para %LOCALAPPDATA%\Programs\Disky\Disky.exe
    - copia icon.ico
    - cria Desktop\Disky.lnk
    - cria Startup\Disky.lnk com --background
    """
    src = current_executable()
    if not os.path.exists(src):
        raise FileNotFoundError(f"Executável não encontrado: {src}")

    install_dir = app_install_dir()
    os.makedirs(install_dir, exist_ok=True)
    dst = installed_exe_path()

    # Se já estiver rodando do local instalado, não copia por cima de si mesmo.
    if os.path.abspath(src).lower() != os.path.abspath(dst).lower():
        shutil.copy2(src, dst)

    # Copia ícone se existir
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dev_icon = os.path.join(root, "build", "icon.ico")
    if os.path.exists(dev_icon):
        shutil.copy2(dev_icon, os.path.join(install_dir, "icon.ico"))

    desktop_dir = get_special_folder("Desktop")
    startup_dir = get_special_folder("Startup")

    desktop_lnk = os.path.join(desktop_dir, "Disky.lnk")
    startup_lnk = os.path.join(startup_dir, "Disky.lnk")

    create_shortcut(desktop_lnk, dst, "", "Disky - Organizador inteligente by PITOCO113 🇧🇷")

    if enable_startup:
        create_shortcut(startup_lnk, dst, "--background", "Disky em segundo plano")
    elif os.path.exists(startup_lnk):
        os.remove(startup_lnk)

    return {
        "install_dir": install_dir,
        "exe": dst,
        "desktop_shortcut": desktop_lnk,
        "startup_shortcut": startup_lnk if enable_startup else None,
    }


def set_startup_enabled(enabled: bool) -> dict:
    target = installed_exe_path()
    if not os.path.exists(target):
        # Se ainda não instalou, instala ao ativar startup.
        if enabled:
            return install_app(enable_startup=True)
        raise FileNotFoundError("Disky ainda não está instalado.")

    startup_dir = get_special_folder("Startup")
    startup_lnk = os.path.join(startup_dir, "Disky.lnk")
    if enabled:
        create_shortcut(startup_lnk, target, "--background", "Disky em segundo plano")
    else:
        if os.path.exists(startup_lnk):
            os.remove(startup_lnk)
    return {"startup_shortcut": startup_lnk, "enabled": enabled}


def is_startup_enabled() -> bool:
    try:
        startup_dir = get_special_folder("Startup")
        return os.path.exists(os.path.join(startup_dir, "Disky.lnk"))
    except Exception:
        return False
