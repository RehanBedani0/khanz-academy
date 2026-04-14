"""
Settings screen for Khan'z Academy Mobile App.

Provides database backup/restore, backup file listing, and app information.
"""

import os

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore
from kivymd.uix.button import MDRaisedButton, MDFlatButton  # type: ignore

from libs.utils import get_backups_path, get_db_path
from widgets.dialogs import (
    show_error_dialog, show_success_dialog, show_confirmation_dialog,
)
from widgets.navigation import BottomNavBar


# App version constant
APP_VERSION: str = "1.0.0"


class SettingsScreen(MDScreen):
    """
    App settings: backup management and application information.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "settings"
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Settings",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(12), dp(12), dp(12), dp(24)],
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # ---- Backup section ----
        content.add_widget(self._section_header("Database Backup"))

        backup_card = MDCard(
            radius=[dp(10)] * 4, elevation=2,
            padding=dp(14), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None, height=dp(110),
        )
        backup_col = MDBoxLayout(orientation="vertical", spacing=dp(8))
        backup_col.add_widget(MDLabel(
            text="Create a timestamped copy of the database in the backups folder.",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None, height=dp(36),
        ))
        backup_btn = MDRaisedButton(
            text="💾  BACKUP NOW",
            md_bg_color=[0.10, 0.45, 0.67, 1],
            size_hint_x=1, height=dp(44),
            on_release=lambda _b: self._do_backup(),
        )
        backup_col.add_widget(backup_btn)
        backup_card.add_widget(backup_col)
        content.add_widget(backup_card)

        # ---- Backup list ----
        content.add_widget(self._section_header("Available Backups"))
        self._backup_list = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
        )
        self._backup_list.bind(minimum_height=self._backup_list.setter("height"))
        content.add_widget(self._backup_list)

        # ---- App info ----
        content.add_widget(self._section_header("App Information"))
        info_card = MDCard(
            radius=[dp(10)] * 4, elevation=2,
            padding=dp(14), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None,
        )
        info_col = MDBoxLayout(orientation="vertical", spacing=dp(6),
                               size_hint_y=None)
        info_col.bind(minimum_height=info_col.setter("height"))

        for label, value in [
            ("App Name",   "KHAN'Z ACADEMY MOBILE APP"),
            ("Version",    APP_VERSION),
            ("Developer",  "Khan'z Academy IT Team"),
            ("DB Path",    get_db_path()),
            ("Backups",    get_backups_path()),
        ]:
            row = MDBoxLayout(orientation="horizontal",
                              size_hint_y=None, height=dp(26))
            row.add_widget(MDLabel(
                text=f"[b]{label}[/b]", markup=True,
                font_style="Body2", theme_text_color="Secondary",
                size_hint_x=0.30,
            ))
            row.add_widget(MDLabel(
                text=str(value), font_style="Body2",
                theme_text_color="Primary", size_hint_x=0.70,
            ))
            info_col.add_widget(row)
        info_card.add_widget(info_col)
        content.add_widget(info_card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(BottomNavBar(active_screen="settings"))
        self.add_widget(root)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _section_header(self, text: str) -> MDLabel:
        return MDLabel(
            text=f"[b]{text}[/b]",
            markup=True,
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_y=None,
            height=dp(30),
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        Clock.schedule_once(lambda _dt: self._load_backups(), 0)

    def _load_backups(self) -> None:
        """Scan the backups folder and display available backup files."""
        self._backup_list.clear_widgets()
        backup_dir = get_backups_path()
        if not os.path.isdir(backup_dir):
            self._backup_list.add_widget(MDLabel(
                text="No backups found.",
                font_style="Body1", theme_text_color="Hint",
                halign="center", size_hint_y=None, height=dp(40),
            ))
            return

        files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith(".db")],
            reverse=True,
        )
        if not files:
            self._backup_list.add_widget(MDLabel(
                text="No backups found.",
                font_style="Body1", theme_text_color="Hint",
                halign="center", size_hint_y=None, height=dp(40),
            ))
            return

        for filename in files:
            full_path = os.path.join(backup_dir, filename)
            size_kb = os.path.getsize(full_path) / 1024
            card = MDCard(
                radius=[dp(8)] * 4, elevation=1,
                padding=dp(10), md_bg_color=[1, 1, 1, 1],
                size_hint_y=None, height=dp(72),
            )
            row = MDBoxLayout(orientation="horizontal", spacing=dp(8))
            info_col = MDBoxLayout(orientation="vertical")
            info_col.add_widget(MDLabel(
                text=filename,
                font_style="Body2", bold=True,
                theme_text_color="Primary",
                size_hint_y=None, height=dp(22),
            ))
            info_col.add_widget(MDLabel(
                text=f"{size_kb:.1f} KB",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None, height=dp(18),
            ))
            restore_btn = MDFlatButton(
                text="RESTORE",
                theme_text_color="Custom",
                text_color=[0.96, 0.26, 0.21, 1],
                size_hint_x=None, width=dp(90),
                on_release=lambda _b, fp=full_path: self._confirm_restore(fp),
            )
            row.add_widget(info_col)
            row.add_widget(restore_btn)
            card.add_widget(row)
            self._backup_list.add_widget(card)

    # ------------------------------------------------------------------
    # Backup / restore
    # ------------------------------------------------------------------

    def _do_backup(self) -> None:
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            show_error_dialog("Error", "Database not available.")
            return
        path = app.db.backup_database()
        if path:
            show_success_dialog("Backup Created", f"Backup saved to:\n{path}")
            Clock.schedule_once(lambda _dt: self._load_backups(), 0.3)
        else:
            show_error_dialog("Backup Failed",
                              "Could not create backup. Check storage permissions.")

    def _confirm_restore(self, backup_path: str) -> None:
        show_confirmation_dialog(
            "Restore Backup",
            "WARNING: This will replace all current data with the selected backup.\n\n"
            "Are you sure you want to continue?",
            on_confirm_callback=lambda: self._do_restore(backup_path),
        )

    def _do_restore(self, backup_path: str) -> None:
        import shutil

        try:
            db_path = get_db_path()
            shutil.copy2(backup_path, db_path)
            # Re-initialise DB manager references
            app = App.get_running_app()
            if app and hasattr(app, "db"):
                app.db.initialise()
            show_success_dialog("Restore Complete",
                                "Database has been restored successfully.\n"
                                "Please restart the app for full effect.")
        except Exception as exc:
            from libs.utils import log_error
            log_error("SettingsScreen._do_restore failed", exc)
            show_error_dialog("Restore Failed",
                              "Could not restore the backup. The file may be corrupted.")

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()
