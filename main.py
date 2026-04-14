"""
KHAN'Z ACADEMY MOBILE APP
==========================
Single entry point — run this file to start the application.

On first launch the app automatically:
    1. Creates required directories (data/, vouchers/, reports/, backups/)
    2. Creates and initialises the SQLite database
    3. Seeds the 12 class records
    4. Opens the Dashboard screen ready to use
"""

import os
import sys

# ---------------------------------------------------------------------------
# Kivy must be configured BEFORE any Kivy imports
# ---------------------------------------------------------------------------
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

import kivy  # noqa: E402
kivy.require("2.1.0")

from kivy.config import Config  # noqa: E402

# Disable desktop-only behaviours for mobile-first experience
Config.set("input", "mouse", "mouse,disable_multitouch")
Config.set("kivy", "window_icon", "")
Config.set("graphics", "resizable", "0")

# ---------------------------------------------------------------------------
# KivyMD App
# ---------------------------------------------------------------------------
from kivymd.app import MDApp  # type: ignore  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.lang import Builder  # noqa: E402
from kivy.uix.screenmanager import ScreenManager, SlideTransition, FadeTransition  # noqa: E402
from kivy.metrics import dp  # noqa: E402

# ---------------------------------------------------------------------------
# Project-local imports
# ---------------------------------------------------------------------------
from libs.utils import ensure_folders_exist, get_base_path  # noqa: E402
from libs.database import DatabaseManager  # noqa: E402

# Screen imports
from screens.dashboard_screen import DashboardScreen  # noqa: E402
from screens.add_student_screen import AddStudentScreen  # noqa: E402
from screens.view_students_screen import ViewStudentsScreen  # noqa: E402
from screens.student_detail_screen import StudentDetailScreen  # noqa: E402
from screens.class_management_screen import ClassManagementScreen  # noqa: E402
from screens.fee_management_screen import FeeManagementScreen  # noqa: E402
from screens.fee_detail_screen import FeeDetailScreen  # noqa: E402
from screens.voucher_screen import VoucherScreen  # noqa: E402
from screens.reports_screen import ReportsScreen  # noqa: E402
from screens.settings_screen import SettingsScreen  # noqa: E402


# ---------------------------------------------------------------------------
# Global KV styling
# ---------------------------------------------------------------------------

_KV_PATH = os.path.join(get_base_path(), "assets", "kv", "style.kv")
if os.path.isfile(_KV_PATH):
    Builder.load_file(_KV_PATH)


# ---------------------------------------------------------------------------
# KhanzAcademyApp
# ---------------------------------------------------------------------------

class KhanzAcademyApp(MDApp):
    """
    Root application class for Khan'z Academy.

    Attributes
    ----------
    db : DatabaseManager
        Shared database manager accessible from all screens via
        ``App.get_running_app().db``.
    selected_student_id : int or None
        Set before navigating to StudentDetailScreen.
    selected_fee_student_id : int or None
        Set before navigating to FeeDetailScreen.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.db: DatabaseManager = None  # type: ignore[assignment]
        self.selected_student_id: int = None  # type: ignore[assignment]
        self.selected_fee_student_id: int = None  # type: ignore[assignment]
        self._screen_history: list = []

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self):
        """Initialise theme, infrastructure, database, and build the UI."""

        # ---- Material theme ----
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "900"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"

        # ---- Ensure required folders exist ----
        ensure_folders_exist()

        # ---- Initialise database ----
        self.db = DatabaseManager()
        self.db.initialise()

        # ---- Build ScreenManager ----
        sm = ScreenManager(transition=SlideTransition(duration=0.25))

        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(AddStudentScreen(name="add_student"))
        sm.add_widget(ViewStudentsScreen(name="view_students"))
        sm.add_widget(StudentDetailScreen(name="student_detail"))
        sm.add_widget(ClassManagementScreen(name="class_management"))
        sm.add_widget(FeeManagementScreen(name="fee_management"))
        sm.add_widget(FeeDetailScreen(name="fee_detail"))
        sm.add_widget(VoucherScreen(name="voucher"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(SettingsScreen(name="settings"))

        sm.current = "dashboard"
        return sm

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def go_to_screen(self, screen_name: str) -> None:
        """
        Navigate forward to *screen_name* with a left-sliding transition.

        Pushes the current screen onto the history stack so that
        ``go_back()`` can return to it.
        """
        sm = self.root
        if sm is None:
            return
        if sm.current == screen_name:
            return
        self._screen_history.append(sm.current)
        sm.transition = SlideTransition(direction="left", duration=0.25)
        sm.current = screen_name

    def go_back(self) -> None:
        """
        Navigate back to the previous screen (right-sliding transition).

        If there is no history, return to the Dashboard.
        """
        sm = self.root
        if sm is None:
            return
        if self._screen_history:
            prev = self._screen_history.pop()
            sm.transition = SlideTransition(direction="right", duration=0.25)
            sm.current = prev
        elif sm.current != "dashboard":
            sm.transition = SlideTransition(direction="right", duration=0.25)
            sm.current = "dashboard"

    # ------------------------------------------------------------------
    # Android back button
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        """Bind the Android back button after the app has started."""
        try:
            from android import activity  # type: ignore
        except ImportError:
            pass  # Not on Android — no action needed

        from kivy.core.window import Window  # local to avoid re-import error
        Window.bind(on_keyboard=self._handle_keyboard)

    def _handle_keyboard(self, _window, key: int, *_args) -> bool:
        """
        Intercept the Android back key (key code 27 / ESC or 1001).

        Returns True to consume the event (prevent default action).
        """
        back_keys = {27, 1001}  # ESC on desktop, Android back button
        if key in back_keys:
            sm = self.root
            if sm and sm.current == "dashboard":
                self._confirm_exit()
            else:
                self.go_back()
            return True
        return False

    def _confirm_exit(self) -> None:
        """Show an exit confirmation dialog when back is pressed on Dashboard."""
        from widgets.dialogs import show_confirmation_dialog

        show_confirmation_dialog(
            title="Exit App",
            message="Are you sure you want to exit KHAN'Z ACADEMY?",
            on_confirm_callback=self._stop_app,
        )

    def _stop_app(self) -> None:
        """Cleanly stop the application."""
        self.stop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    KhanzAcademyApp().run()
