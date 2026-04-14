"""
Dashboard screen for Khan'z Academy Mobile App.
Premium Redesign - Soft Colors, Center Alignment, and Material Icons.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.gridlayout import MDGridLayout  # type: ignore
from kivymd.uix.label import MDLabel, MDIcon  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore

from libs.utils import format_currency, get_current_date, get_month_name, get_current_month_year
from widgets.navigation import BottomNavBar


# ---------------------------------------------------------------------------
# Navigation card data (Upgraded to Material Icons and Soft Colors)
# ---------------------------------------------------------------------------

_NAV_CARDS = [
    {"title": "Students",     "subtitle": "View all students",      "icon": "account-group",      "screen": "view_students",    "color": [0.247, 0.318, 0.710, 1]}, # Indigo
    {"title": "Add Student",  "subtitle": "Enrol a new student",    "icon": "account-plus",       "screen": "add_student",      "color": [0.300, 0.690, 0.310, 1]}, # Soft Green
    {"title": "Fee Mgmt",     "subtitle": "Track payments & fees",  "icon": "credit-card-outline","screen": "fee_management",   "color": [0.950, 0.610, 0.070, 1]}, # Soft Orange
    {"title": "Classes",      "subtitle": "Class-wise listing",     "icon": "google-classroom",   "screen": "class_management", "color": [0.898, 0.224, 0.208, 1]}, # Soft Red
    {"title": "Vouchers",     "subtitle": "Generate fee receipts",  "icon": "receipt",            "screen": "voucher",          "color": [0.000, 0.588, 0.533, 1]}, # Teal
    {"title": "Reports",      "subtitle": "PDF management reports", "icon": "chart-bar",          "screen": "reports",          "color": [0.610, 0.350, 0.710, 1]}, # Soft Purple
    {"title": "Backup",       "subtitle": "Backup your data",       "icon": "content-save",       "screen": "__backup__",       "color": [0.010, 0.660, 0.960, 1]}, # Light Blue
    {"title": "Settings",     "subtitle": "App configuration",      "icon": "cog",                "screen": "settings",         "color": [0.460, 0.460, 0.500, 1]}, # Grey
]


# ---------------------------------------------------------------------------
# Dashboard screen
# ---------------------------------------------------------------------------

class DashboardScreen(MDScreen):
    """
    Main landing screen showing statistics and navigation cards.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "dashboard"
        self._stat_labels: dict = {}
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = MDBoxLayout(orientation="vertical")

        # ---- Top app bar ----
        toolbar = MDTopAppBar(
            title="KHAN'Z ACADEMY",
            md_bg_color=[0.247, 0.318, 0.710, 1], # Soft Indigo 500
            specific_text_color=[1, 1, 1, 1],
            elevation=2, # Softer shadow
        )
        root.add_widget(toolbar)

        # ---- Scrollable content ----
        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12), # Increased spacing for breathing room
            padding=[dp(16), dp(12), dp(16), dp(16)],
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # Date / welcome banner
        month, year = get_current_month_year()
        date_str = get_current_date()
        welcome_card = MDCard(
            radius=[dp(16)] * 4,
            elevation=1.5,
            padding=dp(16),
            size_hint_y=None,
            height=dp(75),
            md_bg_color=[0.247, 0.318, 0.710, 1], # Soft Indigo 500
        )
        welcome_inner = MDBoxLayout(orientation="vertical")
        welcome_inner.add_widget(MDLabel(
            text="Welcome Back!",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            size_hint_y=None,
            height=dp(28),
        ))
        welcome_inner.add_widget(MDLabel(
            text=f"{get_month_name(month)} {year}  |  {date_str}",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.85, 0.90, 1.0, 1],
            size_hint_y=None,
            height=dp(20),
        ))
        welcome_card.add_widget(welcome_inner)
        content.add_widget(welcome_card)

        # ---- Stat cards row ----
        stats_row = MDGridLayout(
            cols=2,
            spacing=dp(12),
            size_hint_y=None,
            height=dp(100),
        )
        stat_defs = [
            ("total_students",   "Total Students",   "0",    [0.247, 0.318, 0.710, 1]), # Indigo
            ("month_collected",  "This Month",       "Rs.0", [0.300, 0.690, 0.310, 1]), # Green
            ("pending_fees",     "Pending Fees",     "Rs.0", [0.898, 0.224, 0.208, 1]), # Red
            ("total_classes",    "Classes",          "12",   [0.950, 0.610, 0.070, 1]), # Orange
        ]
        for key, label, default_val, color in stat_defs:
            card = MDCard(
                radius=[dp(16)] * 4,
                elevation=1.5,
                padding=dp(10),
                md_bg_color=[1, 1, 1, 1],
            )
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            val_lbl = MDLabel(
                text=default_val,
                font_style="H6",
                bold=True,
                theme_text_color="Custom",
                text_color=color,
                size_hint_y=None,
                height=dp(30),
                halign="center",
            )
            cap_lbl = MDLabel(
                text=label,
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20),
                halign="center",
            )
            inner.add_widget(val_lbl)
            inner.add_widget(cap_lbl)
            card.add_widget(inner)
            stats_row.add_widget(card)
            self._stat_labels[key] = val_lbl
        content.add_widget(stats_row)

        # ---- Navigation cards ----
        nav_header = MDLabel(
            text="Quick Navigation",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=[0.247, 0.318, 0.710, 1], # Soft Indigo
            size_hint_y=None,
            height=dp(35),
        )
        content.add_widget(nav_header)

        nav_grid = MDGridLayout(
            cols=2,
            spacing=dp(12),
            size_hint_y=None,
        )
        nav_grid.bind(minimum_height=nav_grid.setter("height"))

        for card_def in _NAV_CARDS:
            nav_card = self._make_nav_card(card_def)
            nav_grid.add_widget(nav_card)
        content.add_widget(nav_grid)

        scroll.add_widget(content)
        root.add_widget(scroll)

        # ---- Bottom navigation ----
        root.add_widget(BottomNavBar(active_screen="dashboard"))

        self.add_widget(root)

    def _make_nav_card(self, card_def: dict) -> MDCard:
        """Return a perfectly centered navigation card widget."""
        card = MDCard(
            radius=[dp(16)] * 4,
            elevation=1.5,
            padding=dp(12),
            size_hint_y=None,
            height=dp(110),
            ripple_behavior=True,
            md_bg_color=[1, 1, 1, 1],
        )
        inner = MDBoxLayout(orientation="vertical", spacing=dp(6))

        # Using MDIcon properly instead of text labels
        icon_lbl = MDIcon(
            icon=card_def["icon"],
            theme_text_color="Custom",
            text_color=card_def["color"],
            halign="center",
            font_size=dp(32),
            size_hint_y=None,
            height=dp(36),
        )
        title_lbl = MDLabel(
            text=card_def["title"],
            font_style="Subtitle2",
            bold=True,
            theme_text_color="Custom",
            text_color=card_def["color"],
            size_hint_y=None,
            height=dp(20),
            halign="center", # Perfectly Centered
        )
        sub_lbl = MDLabel(
            text=card_def["subtitle"],
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(18),
            halign="center", # Perfectly Centered
        )
        inner.add_widget(icon_lbl)
        inner.add_widget(title_lbl)
        inner.add_widget(sub_lbl)
        card.add_widget(inner)

        # Bind tap
        screen_target = card_def["screen"]
        card.bind(on_touch_up=lambda c, t, s=screen_target: self._nav_card_tap(c, t, s))
        return card

    def _nav_card_tap(self, card, touch, screen_target: str) -> None:
        """Handle navigation card tap."""
        if not card.collide_point(*touch.pos):
            return
        app = App.get_running_app()
        if app is None:
            return
        if screen_target == "__backup__":
            self._do_backup()
        else:
            app.go_to_screen(screen_target)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        """Refresh statistics whenever this screen becomes active."""
        Clock.schedule_once(lambda _dt: self._refresh_stats(), 0)

    def _refresh_stats(self) -> None:
        """Load live statistics from the database."""
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        db = app.db
        try:
            # Total students
            count = db.get_student_count()
            self._stat_labels["total_students"].text = str(count)

            # This month collected
            month, year = get_current_month_year()
            month_str = f"{year}-{month:02d}"
            summary = db.get_fee_summary_for_month(month_str)
            self._stat_labels["month_collected"].text = format_currency(
                summary.get("total_collected", 0)
            )
            self._stat_labels["pending_fees"].text = format_currency(
                summary.get("total_pending", 0)
            )
            # Classes always 12
            self._stat_labels["total_classes"].text = "12"
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Backup shortcut
    # ------------------------------------------------------------------

    def _do_backup(self) -> None:
        """Trigger a database backup from the dashboard shortcut."""
        from widgets.dialogs import show_success_dialog, show_error_dialog

        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        path = app.db.backup_database()
        if path:
            show_success_dialog("Backup Successful", f"Saved to:\n{path}")
        else:
            show_error_dialog("Backup Failed", "Could not create backup. Check storage permissions.")
