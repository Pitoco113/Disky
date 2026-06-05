"""
ui/app.py - Interface gráfica principal do Disky
Criado por PITOCO113 🇧🇷
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import subprocess
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db
from core.db import get_config, set_config, get_stats, get_recent_history, get_history_count, get_rules
from core.organizer import organize_folder, get_destination, FolderWatcher
from core.install import install_app, set_startup_enabled, is_startup_enabled, installed_exe_path
from core.duplicate_finder import run_full_scan, group_duplicates, delete_duplicate_file
from locales import I18n

COR_FUNDO = "#1a1a2e"
COR_CARTAO = "#16213e"
COR_PRIMARIA = "#2b7a4b"
COR_SECUNDARIA = "#1a5c3a"
COR_DESTAQUE = "#3a8fd4"


class DiskyApp(ctk.CTk):
    def __init__(self, start_hidden: bool = False):
        super().__init__()
        self.start_hidden = start_hidden

        db.init_db()
        db.seed_default_rules()

        lang = get_config("language", "pt_BR")
        I18n.set_language(lang)
        self.i18n = I18n
        self._lang = lang

        # Garante que Downloads está na lista
        dl = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.isdir(dl) and not any(f["path"] == dl for f in db.get_watched_folders()):
            db.add_watched_folder(dl)

        self.watcher = None
        self._organizing = False
        self._scanning = False

        self.title(self.i18n.t("app_title"))
        self.geometry("900x640")
        self.minsize(780, 540)
        self.configure(fg_color=COR_FUNDO)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_menubar()
        self._build_header()
        self._build_main_area()
        self._build_status_bar()

        self.refresh_dashboard()
        self.refresh_organizer_tab()
        self.refresh_duplicates_tab()

        self.after(1000, self._start_watcher)

        if get_config("wizard_done") == "0" and not self.start_hidden:
            self.after(800, self._show_wizard)

        if self.start_hidden:
            self.after(200, self.withdraw)

    # ─── Watcher ──────────────────────────────────────────────

    def _start_watcher(self):
        try:
            self.watcher = FolderWatcher(self)
            ok = self.watcher.start()
            folders = db.get_watched_folders()
            if ok and folders:
                self._set_status(self.i18n.t("status_monitoring", n=len(folders)))
            else:
                self._set_status("⏸️  Nenhuma pasta sendo monitorada")
        except Exception as e:
            self._set_status(f"⚠️  {str(e)[:40]}")

    # ─── Menu ─────────────────────────────────────────────────

    def _build_menubar(self):
        bar = ctk.CTkFrame(self, fg_color=COR_CARTAO, corner_radius=0, height=36)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(6, weight=1)

        # Idioma
        self.lang_btn = ctk.CTkOptionMenu(
            bar,
            values=[v for _, v in self.i18n.get_languages()],
            command=self._change_lang,
            fg_color="#333", button_color=COR_PRIMARIA,
            button_hover_color=COR_SECUNDARIA,
            width=140, height=28, font=ctk.CTkFont(size=11),
        )
        self.lang_btn.grid(row=0, column=0, padx=(10, 5), pady=2)
        self._update_lang_btn()

        # Botão Instalar
        self.install_btn = ctk.CTkButton(
            bar,
            text="📌  Instalar no Windows",
            command=self._install_windows,
            fg_color="transparent",
            hover_color="#2a2a4a",
            font=ctk.CTkFont(size=12),
            height=28, width=130,
        )
        self.install_btn.grid(row=0, column=1, padx=5, pady=2)

        # Iniciar com Windows toggle
        self.startup_var = ctk.StringVar(value="")
        startup_btn = ctk.CTkSwitch(
            bar,
            text="Iniciar com Windows",
            command=self._toggle_startup,
            font=ctk.CTkFont(size=10),
            progress_color=COR_PRIMARIA,
            onvalue="1", offvalue="0",
        )
        startup_btn.grid(row=0, column=2, padx=5, pady=2)

        # Marca
        ctk.CTkLabel(
            bar,
            text=self.i18n.t("creator_name"),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#888",
        ).grid(row=0, column=6, padx=15, pady=2, sticky="e")

        # Atualiza toggle após criar
        self.after(100, lambda: startup_btn.select() if get_config("run_on_startup", "0") == "1" else startup_btn.deselect())

    def _update_lang_btn(self):
        langs = dict(self.i18n.get_languages())
        self.lang_btn.set(langs.get(self._lang, "🇧🇷  Português"))

    def _change_lang(self, choice):
        lang_map = {"🇧🇷  Português": "pt_BR", "🇺🇸  English": "en"}
        code = lang_map.get(choice, "pt_BR")
        self._lang = code
        self.i18n.set_language(code)
        set_config("language", code)
        self._rebuild_ui()

    def _rebuild_ui(self):
        self.title(self.i18n.t("app_title"))
        self.header_title.configure(text=self.i18n.t("app_title"))
        self.header_sub.configure(text=self.i18n.t("app_subtitle", creator=self.i18n.t("creator_name")))
        self._rebuild_main_area()
        self._update_lang_btn()
        if hasattr(self, '_status_text'):
            self._set_status(self._status_text)

    # ─── Header ───────────────────────────────────────────────

    def _build_header(self):
        h = ctk.CTkFrame(self, fg_color=COR_CARTAO, corner_radius=0)
        h.grid(row=1, column=0, sticky="ew")
        h.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            h, text=self.i18n.t("app_title"),
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COR_PRIMARIA,
        )
        self.header_title.grid(row=0, column=0, pady=(10, 0))

        self.header_sub = ctk.CTkLabel(
            h, text=self.i18n.t("app_subtitle", creator=self.i18n.t("creator_name")),
            font=ctk.CTkFont(size=12), text_color="#888",
        )
        self.header_sub.grid(row=1, column=0, pady=(0, 8))

    # ─── Main Area ────────────────────────────────────────────

    def _build_main_area(self):
        if hasattr(self, 'tabview'):
            self.tabview.destroy()
        self.tabview = ctk.CTkTabview(self, fg_color=COR_FUNDO)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)

        self.tabview.add(self.i18n.t("tab_dashboard"))
        self.tabview.add(self.i18n.t("tab_organizer"))
        self.tabview.add(self.i18n.t("tab_duplicates"))

        self._build_dashboard_tab()
        self._build_organizer_tab()
        self._build_duplicates_tab()

    def _rebuild_main_area(self):
        self._build_main_area()
        self.refresh_dashboard()
        self.refresh_organizer_tab()
        self.refresh_duplicates_tab()

    # ─── Status Bar ───────────────────────────────────────────

    def _build_status_bar(self):
        s = ctk.CTkFrame(self, fg_color=COR_CARTAO, corner_radius=0, height=30)
        s.grid(row=3, column=0, sticky="ew")
        s.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(
            s, text="✅  Pronto!",
            font=ctk.CTkFont(size=11), text_color="#888",
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=4, sticky="w")

    def _set_status(self, msg):
        self._status_text = msg
        self.status_label.configure(text=msg)

    # ─── DASHBOARD ────────────────────────────────────────────

    def _build_dashboard_tab(self):
        tab = self.tabview.tab(self.i18n.t("tab_dashboard"))
        tab.grid_columnconfigure(0, weight=1)

        card_frame = ctk.CTkFrame(tab, fg_color=COR_FUNDO)
        card_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 5))
        card_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_organized = ctk.CTkLabel(
            card_frame, text="📥 0\norganizados",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COR_CARTAO, corner_radius=10,
            width=200, height=80,
        )
        self.card_organized.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.card_duplicates = ctk.CTkLabel(
            card_frame, text="🔁 0\nduplicatas",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COR_CARTAO, corner_radius=10,
            width=200, height=80,
        )
        self.card_duplicates.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.card_space = ctk.CTkLabel(
            card_frame, text="💾 0 MB\nliberados",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COR_CARTAO, corner_radius=10,
            width=200, height=80,
        )
        self.card_space.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        btn_frame = ctk.CTkFrame(tab, fg_color=COR_FUNDO)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_organize = ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn_organize_now"),
            command=self._organize_all,
            fg_color=COR_PRIMARIA, hover_color=COR_SECUNDARIA,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
        )
        self.btn_organize.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_scan = ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn_scan_duplicates"),
            command=self._scan_duplicates,
            fg_color=COR_DESTAQUE, hover_color="#2a6b9c",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
        )
        self.btn_scan.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.hist_frame = ctk.CTkScrollableFrame(tab, fg_color=COR_FUNDO, height=200)
        self.hist_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.hist_frame.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

    def refresh_dashboard(self):
        stats = get_stats()
        self.card_organized.configure(
            text=self.i18n.t("card_organized", count=stats["organized"]))
        self.card_duplicates.configure(
            text=self.i18n.t("card_duplicates",
                count="várias" if stats["space_found_mb"] > 0 else "0"))
        self.card_space.configure(
            text=self.i18n.t("card_space", size=stats["space_found_mb"]))

        for w in self.hist_frame.winfo_children():
            w.destroy()
        history = get_recent_history(15)
        if history:
            ctk.CTkLabel(
                self.hist_frame, text=self.i18n.t("label_recent"),
                font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaa",
            ).grid(row=0, column=0, sticky="w", pady=(5, 2))
            for i, h in enumerate(history):
                ctk.CTkLabel(
                    self.hist_frame, text=f"  • {h['filename']} → {h['rule_name']}",
                    font=ctk.CTkFont(size=11), text_color="#ccc",
                ).grid(row=i+1, column=0, sticky="w", padx=10)
        else:
            ctk.CTkLabel(
                self.hist_frame, text=self.i18n.t("no_activity"),
                font=ctk.CTkFont(size=12), text_color="#666",
            ).grid(row=0, column=0, padx=20, pady=30)

    # ─── ORGANIZER TAB ────────────────────────────────────────

    def _build_organizer_tab(self):
        tab = self.tabview.tab(self.i18n.t("tab_organizer"))
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tab, text=self.i18n.t("watched_folders"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")

        self.folders_frame = ctk.CTkFrame(tab, fg_color=COR_CARTAO, corner_radius=8)
        self.folders_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        self.folders_frame.grid_columnconfigure(0, weight=1)

        add_btn_frame = ctk.CTkFrame(tab, fg_color=COR_FUNDO)
        add_btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        add_btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            add_btn_frame, text=self.i18n.t("btn_add_folder"),
            command=self._add_folder,
            fg_color=COR_PRIMARIA, hover_color=COR_SECUNDARIA,
            font=ctk.CTkFont(size=12), width=160, height=32,
        ).grid(row=0, column=0, padx=2, sticky="w")

        ctk.CTkButton(
            add_btn_frame, text=self.i18n.t("btn_organize"),
            command=self._organize_all,
            fg_color=COR_DESTAQUE, hover_color="#2a6b9c",
            font=ctk.CTkFont(size=12, weight="bold"), width=160, height=32,
        ).grid(row=0, column=1, padx=2, sticky="w")

        ctk.CTkLabel(
            tab, text=self.i18n.t("rules_title"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=3, column=0, padx=10, pady=(10, 2), sticky="w")

        self.rules_frame = ctk.CTkScrollableFrame(tab, fg_color=COR_FUNDO, height=180)
        self.rules_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=2)
        self.rules_frame.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(4, weight=1)

    def refresh_organizer_tab(self):
        for w in self.folders_frame.winfo_children():
            w.destroy()
        folders = db.get_watched_folders()
        if folders:
            for i, f in enumerate(folders):
                lbl = ctk.CTkLabel(
                    self.folders_frame,
                    text=f"  📁  {f['path']}",
                    font=ctk.CTkFont(size=11), anchor="w",
                )
                lbl.grid(row=i, column=0, padx=10, pady=2, sticky="ew")
        else:
            ctk.CTkLabel(
                self.folders_frame,
                text="Nenhuma pasta adicionada.",
                font=ctk.CTkFont(size=11), text_color="#666",
            ).grid(row=0, column=0, padx=10, pady=8)

        for w in self.rules_frame.winfo_children():
            w.destroy()
        rules = get_rules()
        ctk.CTkLabel(
            self.rules_frame,
            text=f"{'Nome':20s} {'Destino':20s} {'Ativa':8s}",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaa",
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        for i, r in enumerate(rules):
            txt = f"{r['name']:15s} → {r['destination']:15s} {'✅' if r['active'] else '❌':8s}"
            ctk.CTkLabel(
                self.rules_frame, text=txt,
                font=ctk.CTkFont(size=11),
            ).grid(row=i+1, column=0, sticky="w", padx=10, pady=1)

    # ─── DUPLICATES TAB ──────────────────────────────────────

    def _build_duplicates_tab(self):
        tab = self.tabview.tab(self.i18n.t("tab_duplicates"))
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        self.dup_info = ctk.CTkLabel(
            tab, text=self.i18n.t("duplicates_space", size="0"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.dup_info.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")

        self.dup_scan_btn = ctk.CTkButton(
            tab, text=self.i18n.t("btn_scan_now"),
            command=self._scan_duplicates,
            fg_color=COR_DESTAQUE, hover_color="#2a6b9c",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=180, height=36,
        )
        self.dup_scan_btn.grid(row=1, column=0, padx=10, pady=2, sticky="w")

        self.dup_frame = ctk.CTkScrollableFrame(tab, fg_color=COR_FUNDO)
        self.dup_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.dup_frame.grid_columnconfigure(0, weight=1)

    def refresh_duplicates_tab(self):
        scan = db.get_last_scan()
        if scan and scan["total_duplicates"] > 0:
            self.dup_info.configure(
                text=self.i18n.t("duplicates_space",
                    size=round(scan["space_wasted_mb"], 1)))
        else:
            self.dup_info.configure(text=self.i18n.t("duplicates_space", size="0"))

        for w in self.dup_frame.winfo_children():
            w.destroy()

        if not scan or scan["total_duplicates"] == 0:
            ctk.CTkLabel(
                self.dup_frame, text="Clique em 'Escanear Agora' para começar",
                font=ctk.CTkFont(size=12), text_color="#666",
            ).grid(row=0, column=0, padx=20, pady=30)
            return

        groups = group_duplicates(scan["id"])
        if not groups:
            ctk.CTkLabel(
                self.dup_frame, text=self.i18n.t("no_duplicates_found"),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COR_PRIMARIA,
            ).grid(row=0, column=0, padx=20, pady=30)
            return

        for i, g in enumerate(groups):
            wasted_mb = round(
                (g["count"] - 1) * (g["total_bytes"] / g["count"]) / (1024*1024), 2)
            card = ctk.CTkFrame(self.dup_frame, fg_color=COR_CARTAO, corner_radius=6)
            card.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                card,
                text=f"{g['filename']} ({g['count']} cópias) → {wasted_mb} MB",
                font=ctk.CTkFont(size=11), anchor="w",
            ).grid(row=0, column=0, padx=8, pady=4, sticky="w")

    # ─── AÇÕES ────────────────────────────────────────────────

    def _add_folder(self):
        folder = filedialog.askdirectory(title="Selecione uma pasta para monitorar")
        if folder:
            db.add_watched_folder(folder)
            self.refresh_organizer_tab()
            if self.watcher:
                self.watcher.restart()
            self._set_status(f"📁  Pasta adicionada: {folder}")

    def _organize_all(self):
        if self._organizing:
            return
        self._organizing = True
        self.btn_organize.configure(state="disabled", text="⏳  Organizando...")

        def do_organize():
            total_moved = 0
            for f in db.get_watched_folders():
                result = organize_folder(f["path"])
                total_moved += result["moved"]
            self.after(0, lambda: self._organize_done(total_moved))

        threading.Thread(target=do_organize, daemon=True).start()

    def _organize_done(self, moved):
        self._organizing = False
        self.btn_organize.configure(state="normal", text=self.i18n.t("btn_organize_now"))
        self._set_status(self.i18n.t("organize_done", moved=moved))
        self.refresh_dashboard()
        messagebox.showinfo("🧹 Disky", self.i18n.t("organize_done", moved=moved))

    def _scan_duplicates(self):
        if self._scanning:
            return
        self._scanning = True
        self.btn_scan.configure(state="disabled", text="⏳  Escaneando...")
        self.dup_scan_btn.configure(state="disabled", text="⏳  Escaneando...")

        folders = [f["path"] for f in db.get_watched_folders()]
        if not folders:
            messagebox.showinfo("", "Adicione uma pasta primeiro!")
            self._scanning = False
            self.btn_scan.configure(state="normal", text=self.i18n.t("btn_scan_duplicates"))
            self.dup_scan_btn.configure(state="normal", text=self.i18n.t("btn_scan_now"))
            return

        def do_scan():
            try:
                scan_id = run_full_scan(folders)
                scan = db.get_last_scan()
                count = scan["total_duplicates"] if scan else 0
                self.after(0, lambda: self._scan_done(count))
            except Exception as e:
                self.after(0, lambda: self._scan_error(str(e)))

        threading.Thread(target=do_scan, daemon=True).start()

    def _scan_done(self, count):
        self._scanning = False
        self.btn_scan.configure(state="normal", text=self.i18n.t("btn_scan_duplicates"))
        self.dup_scan_btn.configure(state="normal", text=self.i18n.t("btn_scan_now"))
        self.refresh_duplicates_tab()
        self.refresh_dashboard()
        self._set_status(f"✅  Scan concluído! {count} grupos encontrados.")
        messagebox.showinfo("🔍 Disky", self.i18n.t("scan_done", count=count))

    def _scan_error(self, msg):
        self._scanning = False
        self.btn_scan.configure(state="normal", text=self.i18n.t("btn_scan_duplicates"))
        self.dup_scan_btn.configure(state="normal", text=self.i18n.t("btn_scan_now"))
        messagebox.showerror("Erro", f"Erro no scan:\n{msg}")

    def on_file_organized(self, filename, rule):
        """Callback do watcher."""
        self.refresh_dashboard()
        self._set_status(f"📥  {filename} → {rule}")

    # ─── Instalação no Windows ─────────────────────────────────

    def _install_windows(self):
        """Instala como app normal do Windows: copia .exe, cria Desktop e Startup."""
        try:
            info = install_app(enable_startup=True)
            set_config("run_on_startup", "1")
            set_config("installed", "1")
            self._set_status("✅  Disky instalado como app do Windows + segundo plano ativado")
            messagebox.showinfo(
                "✅  Disky Instalado!",
                "Agora sim: Disky foi instalado como app normal do Windows!\n\n"
                f"📦  App instalado em:\n{info['exe']}\n\n"
                f"📌  Atalho na Área de Trabalho:\n{info['desktop_shortcut']}\n\n"
                f"🔄  Inicialização automática:\n{info['startup_shortcut']}\n\n"
                "Ao ligar o PC, ele abre escondido e organiza seus Downloads em tempo real.\n"
                "Criado por PITOCO113 🇧🇷"
            )
        except Exception as e:
            messagebox.showerror(
                "Erro na instalação",
                "Não foi possível instalar o Disky.\n\n"
                f"Detalhe: {e}\n\n"
                "Se o antivírus bloquear PowerShell/atalho, me manda esse erro aqui."
            )

    def _toggle_startup(self):
        """Ativa/desativa inicialização automática real na pasta Startup."""
        try:
            current = get_config("run_on_startup", "0") == "1" or is_startup_enabled()
            new_value = not current
            info = set_startup_enabled(new_value)
            set_config("run_on_startup", "1" if new_value else "0")
            if new_value:
                self._set_status(f"🔄  Inicialização automática ATIVADA: {info.get('startup_shortcut', '')}")
            else:
                self._set_status("⏹️  Inicialização automática DESATIVADA")
        except Exception as e:
            self._set_status(f"⚠️  Erro startup: {str(e)[:60]}")
            messagebox.showerror("Erro", f"Não consegui alterar inicialização automática:\n\n{e}")

    # ─── Wizard ────────────────────────────────────────────────

    def _show_wizard(self):
        from ui.wizard import FirstRunWizard
        w = FirstRunWizard(self, self.i18n, callback=self._wizard_done)
        w.focus()

    def _wizard_done(self):
        pass

    # ─── Fechamento ────────────────────────────────────────────

    def _on_close(self):
        """X da janela = esconder e continuar organizando em segundo plano."""
        self.withdraw()
        self._set_status("🟢  Rodando em segundo plano")

    def quit_app(self):
        """Encerra de verdade."""
        if self.watcher:
            self.watcher.stop()
        self.destroy()


if __name__ == "__main__":
    start_hidden = "--background" in sys.argv or "--hidden" in sys.argv
    app = DiskyApp(start_hidden=start_hidden)
    app.mainloop()
