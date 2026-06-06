"""
ui/app.py - Interface gráfica principal do Disky v2.0
Criado por PITOCO113 🇧🇷
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db
from core.db import get_config, set_config, get_stats, get_recent_history, get_history_count, get_rules
from core.organizer import organize_folder, get_destination, FolderWatcher
from core.install import install_app, set_startup_enabled, is_startup_enabled, installed_exe_path
from core.duplicate_finder import run_full_scan, group_duplicates, delete_duplicate_file
from locales import I18n

# ─── Paleta de Cores Moderna ───────────────────────────────
COR_FUNDO = "#0f0f1a"
COR_CARTAO = "#1a1a2e"
COR_CARTAO_HOVER = "#252542"
COR_PRIMARIA = "#6366f1"  # Indigo vibrante
COR_PRIMARIA_HOVER = "#818cf8"
COR_SECUNDARIA = "#22c55e"  # Verde sucesso
COR_DESTAQUE = "#f59e0b"  # Amarelo atenção
COR_TEXTO = "#f1f5f9"
COR_TEXTO_SEC = "#94a3b8"
COR_ERRO = "#ef4444"
COR_BORDA = "#2d2d4a"


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

        self.title("Disky")
        self.geometry("960x700")
        self.minsize(800, 600)
        self.configure(fg_color=COR_FUNDO)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Fonts
        self.font_titulo = ctk.CTkFont(size=26, weight="bold", family="Segoe UI")
        self.font_subtitulo = ctk.CTkFont(size=13, family="Segoe UI")
        self.font_card = ctk.CTkFont(size=15, weight="bold", family="Segoe UI")
        self.font_corpo = ctk.CTkFont(size=12, family="Segoe UI")
        self.font_botao = ctk.CTkFont(size=13, weight="bold", family="Segoe UI")
        self.font_pequeno = ctk.CTkFont(size=11, family="Segoe UI")

        self._build_header()
        self._build_tabs()
        self._build_status_bar()

        self.refresh_dashboard()
        self.refresh_organizer_tab()
        self.refresh_duplicates_tab()

        self.after(1000, self._start_watcher)

        if get_config("wizard_done") == "0" and not self.start_hidden:
            self.after(800, self._show_wizard)

        if self.start_hidden:
            self.after(200, self.withdraw)

    def _start_watcher(self):
        """Inicia o monitoramento de pastas em segundo plano."""
        try:
            from core.organizer import FolderWatcher
            folders = [f["path"] for f in db.get_watched_folders()]
            if not folders:
                return
            self.watcher = FolderWatcher(folders, on_file=self.on_file_organized)
            self.watcher.start()
            self._set_status(self.i18n.t("status_monitoring", n=len(folders)))
        except Exception as e:
            self._set_status(f"⚠️  Watcher error: {e}")

    # ─── Header ────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COR_CARTAO, corner_radius=0, height=70)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Logo + Título
        container = ctk.CTkFrame(header, fg_color="transparent")
        container.pack(side="left", padx=20, pady=10)

        titulo = ctk.CTkLabel(
            container, text="🧹 Disky",
            font=self.font_titulo, text_color=COR_PRIMARIA
        )
        titulo.pack(anchor="w")

        subtitulo = ctk.CTkLabel(
            container, text=self.i18n.t("app_subtitle", creator="PITOCO113 🇧🇷"),
            font=self.font_corpo, text_color=COR_TEXTO_SEC
        )
        subtitulo.pack(anchor="w")

        # Controles à direita
        controles = ctk.CTkFrame(header, fg_color="transparent")
        controles.pack(side="right", padx=15, pady=10)

        # Selector de idioma estilizado
        self.lang_menu = ctk.CTkOptionMenu(
            controles,
            values=[v for _, v in self.i18n.get_languages()],
            command=self._change_lang,
            fg_color=COR_CARTAO, button_color=COR_PRIMARIA,
            button_hover_color=COR_PRIMARIA_HOVER,
            dropdown_fg_color=COR_CARTAO,
            width=130, height=36, font=self.font_corpo,
            corner_radius=8
        )
        self.lang_menu.pack(side="left", padx=5)
        self._update_lang_btn()

        # Botão instalar
        self.install_btn = ctk.CTkButton(
            controles, text="📌",
            command=self._install_windows,
            fg_color="transparent", hover_color=COR_CARTAO_HOVER,
            font=ctk.CTkFont(size=16), width=40, height=36, corner_radius=8
        )
        self.install_btn.pack(side="left", padx=5)

    def _update_lang_btn(self):
        langs = dict(self.i18n.get_languages())
        self.lang_menu.set(langs.get(self._lang, "🇧🇷  Português"))

    def _change_lang(self, choice):
        lang_map = {"🇧🇷  Português": "pt_BR", "🇺🇸  English": "en"}
        code = lang_map.get(choice, "pt_BR")
        self._lang = code
        self.i18n.set_language(code)
        set_config("language", code)
        self.refresh_dashboard()
        self.refresh_organizer_tab()
        self.refresh_duplicates_tab()
        self._update_lang_btn()
        self._set_status(self.i18n.t("status_monitoring", n=len(db.get_watched_folders())))

    # ─── Tabs ──────────────────────────────────────────────────

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(
            self, fg_color=COR_FUNDO,
            segmented_button_fg_color=COR_CARTAO,
            segmented_button_selected_color=COR_PRIMARIA,
            segmented_button_selected_hover_color=COR_PRIMARIA_HOVER,
            segmented_button_unselected_color=COR_CARTAO,
            segmented_button_unselected_hover_color=COR_CARTAO_HOVER,
            corner_radius=10
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        self.tabview.add(self.i18n.t("tab_dashboard"))
        self.tabview.add(self.i18n.t("tab_organizer"))
        self.tabview.add(self.i18n.t("tab_duplicates"))

        self._build_dashboard_tab()
        self._build_organizer_tab()
        self._build_duplicates_tab()

    # ─── Status Bar ───────────────────────────────────────────

    def _build_status_bar(self):
        s = ctk.CTkFrame(self, fg_color=COR_CARTAO, corner_radius=0, height=32)
        s.pack(fill="x", side="bottom")
        s.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            s, text="✅ " + self.i18n.t("status_monitoring", n=0),
            font=self.font_pequeno, text_color=COR_TEXTO_SEC
        )
        self.status_label.pack(side="left", padx=15, pady=4)

        # Indicador de monitoramento
        self.monitor_indicator = ctk.CTkLabel(
            s, text="🟢", font=ctk.CTkFont(size=12)
        )
        self.monitor_indicator.pack(side="right", padx=10, pady=4)

    def _set_status(self, msg):
        self.status_label.configure(text=msg)

    # ─── DASHBOARD ────────────────────────────────────────────

    def _build_dashboard_tab(self):
        tab = self.tabview.tab(self.i18n.t("tab_dashboard"))
        tab.grid_columnconfigure(0, weight=1)

        # Cards de estatísticas
        cards_frame = ctk.CTkFrame(tab, fg_color=COR_FUNDO)
        cards_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 10))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_organized = self._make_card(
            cards_frame, "📥", "0", self.i18n.t("card_organized_count"),
            COR_PRIMARIA, 0
        )
        self.card_duplicates = self._make_card(
            cards_frame, "🔁", "0", self.i18n.t("card_duplicates_count"),
            COR_DESTAQUE, 1
        )
        self.card_space = self._make_card(
            cards_frame, "💾", "0 MB", self.i18n.t("card_space_count"),
            COR_SECUNDARIA, 2
        )

        # Botões de ação
        action_frame = ctk.CTkFrame(tab, fg_color=COR_FUNDO)
        action_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        action_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_organize = ctk.CTkButton(
            action_frame,
            text=self.i18n.t("btn_organize_now"),
            command=self._organize_all,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            font=self.font_botao, height=48, corner_radius=12
        )
        self.btn_organize.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_scan = ctk.CTkButton(
            action_frame,
            text=self.i18n.t("btn_scan_duplicates"),
            command=self._scan_duplicates,
            fg_color=COR_DESTAQUE, hover_color="#d97706",
            font=self.font_botao, height=48, corner_radius=12
        )
        self.btn_scan.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Histórico
        hist_label = ctk.CTkLabel(
            tab, text=self.i18n.t("label_recent"),
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COR_TEXTO
        )
        hist_label.grid(row=2, column=0, sticky="w", padx=15, pady=(10, 5))

        self.hist_frame = ctk.CTkScrollableFrame(
            tab, fg_color=COR_CARTAO, corner_radius=10,
            height=180, border_width=0
        )
        self.hist_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.hist_frame.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(3, weight=1)

    def _make_card(self, parent, icon, value, label, color, column):
        """Cria um card estilizado."""
        card = ctk.CTkFrame(parent, fg_color=COR_CARTAO, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.grid(row=0, column=column, padx=8, pady=5, sticky="ew")

        icon_lbl = ctk.CTkLabel(
            card, text=icon, font=ctk.CTkFont(size=28)
        )
        icon_lbl.pack(pady=(12, 0))

        value_lbl = ctk.CTkLabel(
            card, text=value,
            font=ctk.CTkFont(size=22, weight="bold"), text_color=color
        )
        value_lbl.pack()

        label_lbl = ctk.CTkLabel(
            card, text=label,
            font=self.font_pequeno, text_color=COR_TEXTO_SEC
        )
        label_lbl.pack(pady=(0, 12))

        return value_lbl

    def refresh_dashboard(self):
        stats = get_stats()
        self.card_organized.configure(
            text=str(stats["organized"]))
        self.card_duplicates.configure(
            text=str(stats.get("duplicate_groups", 0)))
        self.card_space.configure(
            text=f"{stats['space_found_mb']} MB")

        for w in self.hist_frame.winfo_children():
            w.destroy()

        history = get_recent_history(15)
        if history:
            for i, h in enumerate(history):
                item = ctk.CTkFrame(self.hist_frame, fg_color="transparent")
                item.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
                item.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    item, text=f"📄 {h['filename']}",
                    font=self.font_corpo, text_color=COR_TEXTO, anchor="w"
                ).grid(row=0, column=0, sticky="w")

                ctk.CTkLabel(
                    item, text=f"→ {h['rule_name']}",
                    font=self.font_pequeno, text_color=COR_PRIMARIA, anchor="e"
                ).grid(row=0, column=1, sticky="e")
        else:
            ctk.CTkLabel(
                self.hist_frame, text=self.i18n.t("no_activity"),
                font=self.font_corpo, text_color=COR_TEXTO_SEC
            ).pack(pady=30)

    # ─── ORGANIZER TAB ────────────────────────────────────────

    def _build_organizer_tab(self):
        tab = self.tabview.tab(self.i18n.t("tab_organizer"))
        tab.grid_columnconfigure(0, weight=1)

        # Seção Pastas
        section_folders = ctk.CTkFrame(tab, fg_color="transparent")
        section_folders.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        section_folders.grid_columnconfigure(0, weight=1)

        header_pastas = ctk.CTkFrame(section_folders, fg_color="transparent")
        header_pastas.grid(row=0, column=0, sticky="ew")
        header_pastas.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_pastas, text=self.i18n.t("watched_folders"),
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COR_TEXTO
        ).grid(row=0, column=0, sticky="w")

        self.btn_add_folder = ctk.CTkButton(
            header_pastas, text="➕",
            command=self._add_folder,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            font=ctk.CTkFont(size=14), width=36, height=36, corner_radius=8
        )
        self.btn_add_folder.grid(row=0, column=1, sticky="e")

        self.folders_card = ctk.CTkFrame(section_folders, fg_color=COR_CARTAO, corner_radius=10)
        self.folders_card.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.folders_card.grid_columnconfigure(0, weight=1)

        # Seção Ações
        actions = ctk.CTkFrame(tab, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        actions.grid_columnconfigure(0, weight=1)

        self.btn_organize_tab = ctk.CTkButton(
            actions,
            text=self.i18n.t("btn_organize"),
            command=self._organize_all,
            fg_color=COR_SECUNDARIA, hover_color="#16a34a",
            font=self.font_botao, height=44, corner_radius=10
        )
        self.btn_organize_tab.grid(row=0, column=0, padx=5, sticky="ew")

        # Seção Regras
        ctk.CTkLabel(
            tab, text=self.i18n.t("rules_title"),
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COR_TEXTO
        ).grid(row=2, column=0, sticky="w", padx=15, pady=(5, 5))

        self.rules_card = ctk.CTkScrollableFrame(
            tab, fg_color=COR_CARTAO, corner_radius=10, height=160
        )
        self.rules_card.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.rules_card.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(3, weight=1)

    def refresh_organizer_tab(self):
        # Limpa folders
        for w in self.folders_card.winfo_children():
            w.destroy()

        folders = db.get_watched_folders()
        if folders:
            for i, f in enumerate(folders):
                item = ctk.CTkFrame(self.folders_card, fg_color=COR_CARTAO_HOVER, corner_radius=6)
                item.grid(row=i, column=0, sticky="ew", padx=5, pady=3)
                item.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    item, text=f"📁  {f['path']}",
                    font=self.font_corpo, text_color=COR_TEXTO, anchor="w"
                ).grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        else:
            ctk.CTkLabel(
                self.folders_card, text=self.i18n.t("no_folders"),
                font=self.font_corpo, text_color=COR_TEXTO_SEC
            ).grid(row=0, column=0, padx=10, pady=15)

        # Limpa regras
        for w in self.rules_card.winfo_children():
            w.destroy()

        rules = get_rules()
        if rules:
            for r in rules:
                item = ctk.CTkFrame(self.rules_card, fg_color=COR_CARTAO_HOVER, corner_radius=6)
                item.pack(fill="x", padx=5, pady=3)

                status_color = COR_SECUNDARIA if r["active"] else COR_TEXTO_SEC
                ctk.CTkLabel(
                    item, text=f"{'✅' if r['active'] else '❌'}  {r['name']}",
                    font=self.font_corpo, text_color=status_color
                ).pack(side="left", padx=10, pady=8)

                ctk.CTkLabel(
                    item, text=f"→ {r['destination']}",
                    font=self.font_pequeno, text_color=COR_TEXTO_SEC
                ).pack(side="right", padx=10, pady=8)

    # ─── DUPLICATES TAB ────────────────────────────────────────

    def _build_duplicates_tab(self):
        tab = self.tabview.tab(self.i18n.t("tab_duplicates"))
        tab.grid_columnconfigure(0, weight=1)

        # Info card
        info_frame = ctk.CTkFrame(tab, fg_color=COR_CARTAO, corner_radius=12)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        self.dup_info = ctk.CTkLabel(
            info_frame, text=self.i18n.t("duplicates_space", size="0"),
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COR_TEXTO
        )
        self.dup_info.pack(pady=12, padx=15)

        # Botão scan
        scan_frame = ctk.CTkFrame(tab, fg_color="transparent")
        scan_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        scan_frame.grid_columnconfigure(0, weight=1)

        self.dup_scan_btn = ctk.CTkButton(
            scan_frame,
            text=self.i18n.t("btn_scan_now"),
            command=self._scan_duplicates,
            fg_color=COR_DESTAQUE, hover_color="#d97706",
            font=self.font_botao, height=44, corner_radius=10
        )
        self.dup_scan_btn.grid(row=0, column=0, padx=5, sticky="ew")

        # Lista de duplicatas
        self.dup_list = ctk.CTkScrollableFrame(
            tab, fg_color=COR_CARTAO, corner_radius=10
        )
        self.dup_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.dup_list.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

    def refresh_duplicates_tab(self):
        scan = db.get_last_scan()
        if scan and scan["total_duplicates"] > 0:
            self.dup_info.configure(
                text=self.i18n.t("duplicates_space", size=round(scan["space_wasted_mb"], 1)))
        else:
            self.dup_info.configure(text=self.i18n.t("duplicates_space", size="0"))

        for w in self.dup_list.winfo_children():
            w.destroy()

        if not scan or scan["total_duplicates"] == 0:
            ctk.CTkLabel(
                self.dup_list, text=self.i18n.t("no_duplicates_found"),
                font=ctk.CTkFont(size=14, weight="bold"), text_color=COR_SECUNDARIA
            ).pack(pady=40)
            return

        groups = group_duplicates(scan["id"])
        if not groups:
            ctk.CTkLabel(
                self.dup_list, text=self.i18n.t("no_duplicates_found"),
                font=ctk.CTkFont(size=14, weight="bold"), text_color=COR_SECUNDARIA
            ).pack(pady=40)
            return

        for g in groups:
            wasted_mb = round((g["count"] - 1) * (g["total_bytes"] / g["count"]) / (1024*1024), 2)
            card = ctk.CTkFrame(self.dup_list, fg_color=COR_CARTAO_HOVER, corner_radius=8)
            card.pack(fill="x", padx=5, pady=4)

            ctk.CTkLabel(
                card,
                text=f"🔁 {g['filename']} ({g['count']} cópias) — {wasted_mb} MB",
                font=self.font_corpo, text_color=COR_TEXTO, anchor="w"
            ).pack(fill="x", padx=12, pady=10)

    # ─── AÇÕES ────────────────────────────────────────────────

    def _add_folder(self):
        folder = filedialog.askdirectory(title=self.i18n.t("select_folder"))
        if folder:
            db.add_watched_folder(folder)
            self.refresh_organizer_tab()
            if self.watcher:
                self.watcher.restart()
            self._set_status(f"📁  {self.i18n.t('folder_added')}: {folder}")

    def _organize_all(self):
        if self._organizing:
            return
        self._organizing = True
        self.btn_organize.configure(state="disabled", text="⏳  " + self.i18n.t("organizing"))
        self.btn_organize_tab.configure(state="disabled", text="⏳  " + self.i18n.t("organizing"))

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
        self.btn_organize_tab.configure(state="normal", text=self.i18n.t("btn_organize"))
        self._set_status(self.i18n.t("organize_done", moved=moved))
        self.refresh_dashboard()
        messagebox.showinfo("🧹 Disky", self.i18n.t("organize_done", moved=moved))

    def _scan_duplicates(self):
        if self._scanning:
            return
        self._scanning = True
        self.btn_scan.configure(state="disabled", text="⏳  " + self.i18n.t("scanning"))
        self.dup_scan_btn.configure(state="disabled", text="⏳  " + self.i18n.t("scanning"))

        folders = [f["path"] for f in db.get_watched_folders()]
        if not folders:
            self._scanning = False
            self.btn_scan.configure(state="normal", text=self.i18n.t("btn_scan_duplicates"))
            self.dup_scan_btn.configure(state="normal", text=self.i18n.t("btn_scan_now"))
            messagebox.showinfo("", self.i18n.t("no_folder_selected"))
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
        self._set_status(self.i18n.t("scan_done_status", count=count))
        messagebox.showinfo("🔍 Disky", self.i18n.t("scan_done", count=count))

    def _scan_error(self, msg):
        self._scanning = False
        self.btn_scan.configure(state="normal", text=self.i18n.t("btn_scan_duplicates"))
        self.dup_scan_btn.configure(state="normal", text=self.i18n.t("btn_scan_now"))
        messagebox.showerror(self.i18n.t("error"), msg)

    def on_file_organized(self, filename, rule):
        """Callback do watcher."""
        self.refresh_dashboard()
        self._set_status(f"📥  {filename} → {rule}")

    # ─── Instalação ────────────────────────────────────────────

    def _install_windows(self):
        try:
            info = install_app(enable_startup=True)
            set_config("run_on_startup", "1")
            set_config("installed", "1")
            self._set_status(self.i18n.t("installed_msg"))
            messagebox.showinfo(
                self.i18n.t("installed_title"),
                self.i18n.t("installed_body", exe=info['exe'], desktop=info.get('desktop_shortcut', ''))
            )
        except Exception as e:
            messagebox.showerror(self.i18n.t("error"), f"{self.i18n.t('install_error')}\n\n{e}")

    # ─── Wizard ────────────────────────────────────────────────

    def _show_wizard(self):
        from ui.wizard import FirstRunWizard
        w = FirstRunWizard(self, self.i18n, callback=self._wizard_done)
        w.focus()

    def _wizard_done(self):
        pass

    # ─── Fechamento ────────────────────────────────────────────

    def _on_close(self):
        self.withdraw()
        self._set_status("🟢  " + self.i18n.t("running_bg"))

    def quit_app(self):
        if self.watcher:
            self.watcher.stop()
        self.destroy()


if __name__ == "__main__":
    start_hidden = "--background" in sys.argv or "--hidden" in sys.argv
    app = DiskyApp(start_hidden=start_hidden)
    app.mainloop()