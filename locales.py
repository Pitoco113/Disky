"""
locales.py - Sistema de tradução do Disky
Criado por PITOCO113 🇧🇷
"""


class LangPT_BR:
    @staticmethod
    def get() -> dict:
        return {
            "app_title": "🧹  DISKY",
            "app_subtitle": "Organizador inteligente de arquivos  |  Criado por {creator}",
            "creator_name": "PITOCO113 🇧🇷",

            # Dashboard
            "btn_organize_now": "📂  ORGANIZAR TUDO AGORA",
            "btn_scan_duplicates": "🔍  ESCANEAR DUPLICATAS",
            "btn_settings": "⚙️  Configurações",
            "card_organized": "📥 {count} arquivos\norganizados",
            "card_duplicates": "🔁 {count} duplicatas\nencontradas",
            "card_space": "💾 {size} MB\nliberados",
            "label_recent": "🕐  Últimas organizações:",
            "label_stats": "📊  Estatísticas desde o início:",
            "no_activity": "Nenhuma atividade ainda.\nAdicione uma pasta para monitorar!",
            "history_item": "• {file} → {rule}",

            # Abas
            "tab_dashboard": "🏠  Início",
            "tab_organizer": "📥  Organizador",
            "tab_duplicates": "🔁  Duplicatas",

            # Organizer Tab
            "organizer_title": "📥  Organizador de Downloads",
            "watched_folders": "Pastas monitoradas:",
            "btn_add_folder": "➕  Adicionar Pasta",
            "btn_remove_folder": "Remover",
            "btn_organize": "📂  ORGANIZAR TUDO AGORA",
            "btn_pause": "⏸️  Pausar Monitor",
            "btn_resume": "▶️  Retomar Monitor",
            "rules_title": "📋  Regras de Organização",
            "rule_name": "Nome",
            "rule_extensions": "Extensões",
            "rule_destination": "Destino",
            "rule_active": "Ativo",
            "btn_add_rule": "➕  Nova Regra",
            "btn_delete_rule": "🗑️",
            "organizing_progress": "Organizando... ({current}/{total})",
            "organize_done": "✅  Organização concluída! {moved} arquivos movidos.",
            "status_monitoring": "🟢  Monitorando {n} pastas...",
            "status_paused": "⏸️  Monitor pausado",

            # Duplicates Tab
            "duplicates_title": "🔁  Caçador de Duplicatas",
            "duplicates_space": "💾 Espaço que pode liberar: {size} MB",
            "last_scan": "Último scan: {date}",
            "never_scanned": "Nunca escaneado",
            "scanning_progress": "Escaneando... ({current}/{total})",
            "scan_done": "✅  Scan concluído! {count} grupos de duplicatas encontrados.",
            "btn_scan_now": "🔍  Escanear Agora",
            "btn_delete_selected": "🗑️  Limpar Selecionados",
            "duplicate_group": "{file} ({count} cópias) → {size} MB",
            "no_duplicates_found": "🎉  Nenhuma duplicata encontrada!",
            "btn_delete": "Deletar",
            "delete_confirm_title": "Deletar",
            "delete_confirm_msg": "Tem certeza que quer deletar este arquivo?\n\n{filepath}\n\nEle irá para a Lixeira.",

            # Settings Tab
            "settings_title": "⚙️  Configurações",
            "general_title": "Geral",
            "language_label": "Idioma:",
            "auto_organize_label": "Organizar automaticamente:",
            "run_on_startup_label": "Iniciar com o Windows:",
            "desktop_shortcut": "📌  Instalar na Área de Trabalho",
            "btn_save": "💾  Salvar Configurações",
            "settings_saved": "✅  Configurações salvas!",

            # Wizard
            "wizard_title": "👋  Bem-vindo ao Disky!",
            "wizard_desc": "Vou organizar seus Downloads e encontrar arquivos duplicados.\nTudo automático, sem esforço.",
            "wizard_step1": "Passo 1: Escolha as pastas",
            "wizard_step1_desc": "Por padrão, o Disky monitora sua pasta de Downloads.\n\nVocê pode adicionar outras pastas depois.",
            "wizard_step2": "Passo 2: Ative o monitoramento",
            "wizard_step2_desc": "Quando você baixar arquivos, o Disky vai\norganizar automaticamente nas pastas certas.\n\nPDF vai pra Documentos, fotos pra Imagens, etc.",
            "wizard_step3": "Passo 3: Escaneie duplicatas",
            "wizard_step3_desc": "O Disky também encontra arquivos repetidos\nque estão ocupando espaço à toa.\n\nRecomendo escanear agora mesmo!",
            "wizard_final": "✅  Tudo pronto!",
            "wizard_final_desc": "O Disky está configurado.\n\nEle vai ficar na bandeja do sistema 🧹\ne trabalhar em segundo plano.\n\nCriado por PITOCO113 🇧🇷",
            "wizard_btn_start": "▶️  Vamos lá!",
            "wizard_btn_next": "Próximo →",
            "wizard_btn_prev": "← Anterior",
            "wizard_btn_finish": "✅  Começar!",
            "wizard_skip": "Pular",
            "wizard_dont_show": "Não mostrar novamente",
            "wizard_scan_now": "🔍  Escanear agora",
            "wizard_scan_later": "Depois",

            # Bandeja
            "tray_open": "Abrir Disky",
            "tray_organize": "Organizar Agora",
            "tray_pause": "Pausar",
            "tray_resume": "Retomar",
            "tray_exit": "Sair",
        }


class LangEN:
    @staticmethod
    def get() -> dict:
        return {
            "app_title": "🧹  DISKY",
            "app_subtitle": "Smart file organizer  |  Created by {creator}",
            "creator_name": "PITOCO113 🇧🇷",

            "btn_organize_now": "📂  ORGANIZE NOW",
            "btn_scan_duplicates": "🔍  SCAN DUPLICATES",
            "btn_settings": "⚙️  Settings",
            "card_organized": "📥 {count} files\norganized",
            "card_duplicates": "🔁 {count} duplicates\nfound",
            "card_space": "💾 {size} MB\nfreed",
            "label_recent": "🕐  Recent activity:",
            "label_stats": "📊  Stats since start:",
            "no_activity": "No activity yet.\nAdd a folder to watch!",
            "history_item": "• {file} → {rule}",

            "tab_dashboard": "🏠  Home",
            "tab_organizer": "📥  Organizer",
            "tab_duplicates": "🔁  Duplicates",

            "organizer_title": "📥  Download Organizer",
            "watched_folders": "Watched folders:",
            "btn_add_folder": "➕  Add Folder",
            "btn_remove_folder": "Remove",
            "btn_organize": "📂  ORGANIZE NOW",
            "btn_pause": "⏸️  Pause Monitor",
            "btn_resume": "▶️  Resume Monitor",
            "rules_title": "📋  Organization Rules",
            "rule_name": "Name",
            "rule_extensions": "Extensions",
            "rule_destination": "Destination",
            "rule_active": "Active",
            "btn_add_rule": "➕  New Rule",
            "btn_delete_rule": "🗑️",
            "organizing_progress": "Organizing... ({current}/{total})",
            "organize_done": "✅  Done! {moved} files organized.",
            "status_monitoring": "🟢  Watching {n} folders...",
            "status_paused": "⏸️  Monitor paused",

            "duplicates_title": "🔁  Duplicate Finder",
            "duplicates_space": "💾 Space you can free: {size} MB",
            "last_scan": "Last scan: {date}",
            "never_scanned": "Never scanned",
            "scanning_progress": "Scanning... ({current}/{total})",
            "scan_done": "✅  Scan complete! {count} duplicate groups found.",
            "btn_scan_now": "🔍  Scan Now",
            "btn_delete_selected": "🗑️  Clean Selected",
            "duplicate_group": "{file} ({count} copies) → {size} MB",
            "no_duplicates_found": "🎉  No duplicates found!",
            "btn_delete": "Delete",
            "delete_confirm_title": "Delete",
            "delete_confirm_msg": "Are you sure you want to delete this file?\n\n{filepath}\n\nIt will go to Recycle Bin.",

            "settings_title": "⚙️  Settings",
            "general_title": "General",
            "language_label": "Language:",
            "auto_organize_label": "Auto-organize:",
            "run_on_startup_label": "Run on startup:",
            "desktop_shortcut": "📌  Install to Desktop",
            "btn_save": "💾  Save Settings",
            "settings_saved": "✅  Settings saved!",

            "wizard_title": "👋  Welcome to Disky!",
            "wizard_desc": "I'll organize your Downloads and find duplicate files.\nAll automatic, no effort needed.",
            "wizard_step1": "Step 1: Choose folders",
            "wizard_step1_desc": "By default, Disky watches your Downloads folder.\n\nYou can add more folders later.",
            "wizard_step2": "Step 2: Enable monitoring",
            "wizard_step2_desc": "When you download files, Disky will\nautomatically sort them into the right folders.\n\nPDF goes to Documents, photos to Images, etc.",
            "wizard_step3": "Step 3: Scan duplicates",
            "wizard_step3_desc": "Disky also finds duplicate files\nthat are wasting your disk space.\n\nI recommend scanning right now!",
            "wizard_final": "✅  All set!",
            "wizard_final_desc": "Disky is configured.\n\nIt will stay in your system tray 🧹\nand work in the background.\n\nCreated by PITOCO113 🇧🇷",
            "wizard_btn_start": "▶️  Let's Go!",
            "wizard_btn_next": "Next →",
            "wizard_btn_prev": "← Previous",
            "wizard_btn_finish": "✅  Get Started!",
            "wizard_skip": "Skip",
            "wizard_dont_show": "Don't show again",
            "wizard_scan_now": "🔍  Scan now",
            "wizard_scan_later": "Later",

            "tray_open": "Open Disky",
            "tray_organize": "Organize Now",
            "tray_pause": "Pause",
            "tray_resume": "Resume",
            "tray_exit": "Exit",
        }


class I18n:
    _current_lang = "pt_BR"
    _translations = {
        "pt_BR": LangPT_BR.get(),
        "en": LangEN.get(),
    }

    @classmethod
    def set_language(cls, lang: str):
        if lang in cls._translations:
            cls._current_lang = lang

    @classmethod
    def get_language(cls) -> str:
        return cls._current_lang

    @classmethod
    def t(cls, key: str, **kwargs) -> str:
        text = cls._translations[cls._current_lang].get(key, f"[{key}]")
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                pass
        return text

    @classmethod
    def get_languages(cls) -> list:
        return [
            ("pt_BR", "🇧🇷  Português"),
            ("en", "🇺🇸  English"),
        ]