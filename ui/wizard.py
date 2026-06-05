"""
ui/wizard.py - Assistente de boas-vindas do Disky
Criado por PITOCO113 🇧🇷
"""

import customtkinter as ctk

from core.db import set_config, add_watched_folder


class FirstRunWizard(ctk.CTkToplevel):
    def __init__(self, parent, i18n, callback=None):
        super().__init__(parent)
        self.i18n = i18n
        self.callback = callback
        self.step = 0

        self.title(i18n.t("wizard_title"))
        self.geometry("580x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.configure(fg_color="#1a1a2e")

        self._build_ui()
        self._show_step(0)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # Progresso
        self.prog = ctk.CTkFrame(self, fg_color="transparent")
        self.prog.grid(row=0, column=0, pady=(20, 5))
        self.dots = []
        for i in range(4):
            d = ctk.CTkLabel(self.prog, text="○", font=ctk.CTkFont(size=18), text_color="#444")
            d.grid(row=0, column=i, padx=6)
            self.dots.append(d)

        # Conteúdo
        self.content = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        self.content.grid(row=1, column=0, sticky="nsew", padx=30, pady=5)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.content, text="", font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#2b7a4b", wraplength=480, justify="center",
        )
        self.title_lbl.grid(row=0, column=0, pady=(20, 8), padx=20)

        self.desc_lbl = ctk.CTkLabel(
            self.content, text="", font=ctk.CTkFont(size=13),
            text_color="#ccc", wraplength=460, justify="left",
        )
        self.desc_lbl.grid(row=1, column=0, pady=(0, 15), padx=25, sticky="nsew")

        # Botões
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, pady=(8, 15))
        self.btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.prev_btn = ctk.CTkButton(
            self.btn_frame, text="← Anterior", width=110,
            fg_color="#333", hover_color="#555",
            font=ctk.CTkFont(size=12), command=self._prev,
        )
        self.prev_btn.grid(row=0, column=0, padx=4)

        self.next_btn = ctk.CTkButton(
            self.btn_frame, text="Próximo →", width=110,
            fg_color="#2b7a4b", hover_color="#1a5c3a",
            font=ctk.CTkFont(size=12, weight="bold"), command=self._next,
        )
        self.next_btn.grid(row=0, column=2, padx=4)

    def _show_step(self, s):
        self.step = s
        steps = [
            {"title": self.i18n.t("wizard_step1"), "desc": self.i18n.t("wizard_step1_desc")},
            {"title": self.i18n.t("wizard_step2"), "desc": self.i18n.t("wizard_step2_desc")},
            {"title": self.i18n.t("wizard_step3"), "desc": self.i18n.t("wizard_step3_desc")},
            {"title": self.i18n.t("wizard_final"), "desc": self.i18n.t("wizard_final_desc")},
        ]
        info = steps[s]
        self.title_lbl.configure(text=info["title"])
        self.desc_lbl.configure(text=info["desc"])

        for i, d in enumerate(self.dots):
            if i == s:
                d.configure(text="●", text_color="#2b7a4b")
            elif i < s:
                d.configure(text="✓", text_color="#2b7a4b")
            else:
                d.configure(text="○", text_color="#444")

        self.prev_btn.configure(state="normal" if s > 0 else "disabled")
        if s >= 3:
            self.next_btn.configure(text="✅  Começar!", command=self._finish)
        else:
            self.next_btn.configure(text="Próximo →" if self.i18n.get_language() == "pt_BR" else "Next →", command=self._next)

    def _next(self):
        self._show_step(self.step + 1)

    def _prev(self):
        self._show_step(self.step - 1)

    def _finish(self):
        # Adiciona Downloads como pasta monitorada
        dl = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.isdir(dl):
            add_watched_folder(dl)
        set_config("wizard_done", "1")
        self.destroy()
        if self.callback:
            self.callback()

import os