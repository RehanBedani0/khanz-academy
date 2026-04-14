"""
Dashboard screen for Khan'z Academy Mobile App.

Displays summary statistics and a navigation card grid.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.gridlayout import MDGridLayout  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore

from libs.utils import format_currency, get_current_date, get_month_name, get_current_month_year
from widgets.navigation import BottomNavBar


# ---------------------------------------------------------------------------
# Navigation card data
# ---------------------------------------------------------------------------

_NAV_CARDS = [
    {"title": "Students",     "subtitle": "View all students",      "icon": "👥", "screen": "view_students",    "color": [0.10, 0.14, 0.49, 1]},
    {"title": "Add Student",  "subtitle": "Enrol a new student",    "icon": "➕", "screen": "add_student",       "color": [0.23, 0.62, 0.27, 1]},
    {"title": "Fee Mgmt",     "subtitle": "Track payments & fees",  "icon": "💳", "screen": "fee_management",    "color": [0.80, 0.51, 0.01, 1]},
    {"title": "Classes",      "subtitle": "Class-wise listing",     "icon": "🏫", "screen": "class_management",  "color": [0.62, 0.04, 0.23, 1]},
    {"title": "Vouchers",     "subtitle": "Generate fee receipts",  "icon": "🧾", "screen": "voucher",           "color": [0.00, 0.51, 0.50, 1]},
    {"title": "Reports",      "subtitle": "PDF management reports", "icon": "📊", "screen": "reports",           "color": [0.46, 0.10, 0.75, 1]},
    {"title": "Backup",       "subtitle": "Backup your data",       "icon": "💾", "screen": "__backup__",        "color": [0.10, 0.45, 0.67, 1]},
    {"title": "Settings",     "subtitle": "App configuration",      "icon": "⚙️", "screen": "settings",          "color": [0.33, 0.33, 0.33, 1]},
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
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            elevation=4,
        )
        root.add_widget(toolbar)

        # ---- Scrollable content ----
        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # Date / welcome banner
        month, year = get_current_month_year()
        date_str = get_current_date()
        welcome_card = MDCard(
            radius=[dp(12)] * 4,
            elevation=2,
            padding=dp(14),
            size_hint_y=None,
            height=dp(64),
            md_bg_color=[0.10, 0.14, 0.49, 1],
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
            text_color=[0.8, 0.8, 1.0, 1],
            size_hint_y=None,
            height=dp(20),
        ))
        welcome_card.add_widget(welcome_inner)
        content.add_widget(welcome_card)

        # ---- Stat cards row ----
        stats_row = MDGridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(100),
        )
        stat_defs = [
            ("total_students",   "Total Students",   "0",    [0.10, 0.14, 0.49, 1]),
            ("month_collected",  "This Month",        "Rs.0", [0.23, 0.62, 0.27, 1]),
            ("pending_fees",     "Pending Fees",      "Rs.0", [0.96, 0.26, 0.21, 1]),
            ("total_classes",    "Classes",           "12",   [0.80, 0.51, 0.01, 1]),
        ]
        for key, label, default_val, color in stat_defs:
            card = MDCard(
                radius=[dp(10)] * 4,
                elevation=2,
                padding=dp(10),
                md_bg_color=[1, 1, 1, 1],
            )
            inner = MDBoxLayout(orientation="vertical")
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
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_y=None,
            height=dp(30),
        )
        content.add_widget(nav_header)

        nav_grid = MDGridLayout(
            cols=2,
            spacing=dp(8),
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
        """Return a navigation card widget for one shortcut."""
        card = MDCard(
            radius=[dp(12)] * 4,
            elevation=2,
            padding=dp(14),
            size_hint_y=None,
            height=dp(100),
            ripple_behavior=True,
            md_bg_color=[1, 1, 1, 1],
        )
        inner = MDBoxLayout(orientation="vertical", spacing=dp(4))

        icon_lbl = MDLabel(
            text=card_def["icon"],
            font_style="H5",
            size_hint_y=None,
            height=dp(36),
            halign="left",
        )
        title_lbl = MDLabel(
            text=card_def["title"],
            font_style="Subtitle2",
            bold=True,
            theme_text_color="Custom",
            text_color=card_def["color"],
            size_hint_y=None,
            height=dp(22),
        )
        sub_lbl = MDLabel(
            text=card_def["subtitle"],
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(18),
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
