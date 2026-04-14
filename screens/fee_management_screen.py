"""
Fee Management screen for Khan'z Academy Mobile App.

Month/year picker, fee generation, summary stats, and per-student fee list.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDFlatButton, MDRaisedButton  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.gridlayout import MDGridLayout  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.menu import MDDropdownMenu  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore

from libs.utils import (
    format_currency, format_month_year,
    get_current_month_year, get_month_name,
)
from widgets.custom_widgets import KAFeeRow
from widgets.dialogs import show_info_dialog, show_error_dialog
from widgets.navigation import BottomNavBar


# ---------------------------------------------------------------------------
# FeeManagementScreen
# ---------------------------------------------------------------------------

class FeeManagementScreen(MDScreen):
    """
    Central fee management hub with month selection and payment status view.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "fee_management"
        month, year = get_current_month_year()
        self._selected_month: int = month
        self._selected_year: int = year
        self._status_filter: str = "All"
        self._month_menu: MDDropdownMenu = None  # type: ignore[assignment]
        self._year_menu: MDDropdownMenu = None   # type: ignore[assignment]
        self._stat_labels: dict = {}
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Fee Management",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(12), dp(10), dp(12), dp(20)],
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # ---- Month / year selector ----
        month_year_card = MDCard(
            radius=[dp(10)] * 4, elevation=2,
            padding=dp(12), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None, height=dp(100),
        )
        my_col = MDBoxLayout(orientation="vertical", spacing=dp(6))

        my_col.add_widget(MDLabel(
            text="Select Month & Year",
            font_style="Subtitle2",
            bold=True,
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_y=None, height=dp(22),
        ))
        picker_row = MDBoxLayout(
            orientation="horizontal", spacing=dp(8),
            size_hint_y=None, height=dp(44),
        )
        self._month_btn = MDRaisedButton(
            text=get_month_name(self._selected_month),
            md_bg_color=[0.10, 0.14, 0.49, 0.1],
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=0.55,
            height=dp(40),
            on_release=self._open_month_menu,
        )
        self._year_btn = MDRaisedButton(
            text=str(self._selected_year),
            md_bg_color=[0.10, 0.14, 0.49, 0.1],
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=0.45,
            height=dp(40),
            on_release=self._open_year_menu,
        )
        picker_row.add_widget(self._month_btn)
        picker_row.add_widget(self._year_btn)
        my_col.add_widget(picker_row)
        month_year_card.add_widget(my_col)
        content.add_widget(month_year_card)

        # ---- Generate Fees button ----
        gen_btn = MDRaisedButton(
            text="⚡  GENERATE FEES FOR SELECTED MONTH",
            md_bg_color=[0.23, 0.62, 0.27, 1],
            size_hint_x=1,
            height=dp(48),
            on_release=lambda _b: self._generate_fees(),
        )
        content.add_widget(gen_btn)

        # ---- Summary stat cards ----
        stats_grid = MDGridLayout(
            cols=2, spacing=dp(8),
            size_hint_y=None, height=dp(100),
        )
        stat_defs = [
            ("students",   "Students",       "0",    [0.10, 0.14, 0.49, 1]),
            ("expected",   "Expected",        "Rs.0", [0.23, 0.62, 0.27, 1]),
            ("collected",  "Collected",       "Rs.0", [0.46, 0.10, 0.75, 1]),
            ("pending",    "Pending",         "Rs.0", [0.96, 0.26, 0.21, 1]),
        ]
        for key, label, default_val, color in stat_defs:
            card = MDCard(
                radius=[dp(10)] * 4, elevation=2,
                padding=dp(10), md_bg_color=[1, 1, 1, 1],
            )
            inner = MDBoxLayout(orientation="vertical")
            val_lbl = MDLabel(
                text=default_val,
                font_style="H6", bold=True,
                theme_text_color="Custom", text_color=color,
                size_hint_y=None, height=dp(30), halign="center",
            )
            cap_lbl = MDLabel(
                text=label, font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None, height=dp(20), halign="center",
            )
            inner.add_widget(val_lbl)
            inner.add_widget(cap_lbl)
            card.add_widget(inner)
            stats_grid.add_widget(card)
            self._stat_labels[key] = val_lbl
        content.add_widget(stats_grid)

        # ---- Status filter buttons ----
        filter_row = MDBoxLayout(
            orientation="horizontal", spacing=dp(4),
            size_hint_y=None, height=dp(44),
        )
        self._filter_buttons = {}
        for status in ("All", "Paid", "Unpaid", "Partial"):
            btn = MDFlatButton(
                text=status,
                theme_text_color="Custom",
                text_color=[0.10, 0.14, 0.49, 1],
                size_hint_x=0.25,
                on_release=lambda _b, s=status: self._set_status_filter(s),
            )
            filter_row.add_widget(btn)
            self._filter_buttons[status] = btn
        self._highlight_filter_btn("All")
        content.add_widget(filter_row)

        # ---- Fee list ----
        self._fee_list = MDBoxLayout(
            orientation="vertical", spacing=dp(6),
            size_hint_y=None,
        )
        self._fee_list.bind(minimum_height=self._fee_list.setter("height"))
        content.add_widget(self._fee_list)

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(BottomNavBar(active_screen="fee_management"))
        self.add_widget(root)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        Clock.schedule_once(lambda _dt: self._refresh(), 0)

    def _refresh(self) -> None:
        self._load_summary()
        self._load_fee_list()

    # ------------------------------------------------------------------
    # Month / year picker menus
    # ------------------------------------------------------------------

    def _open_month_menu(self, btn) -> None:
        items = [
            {
                "text": get_month_name(m),
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda m=m: self._select_month(m),
            }
            for m in range(1, 13)
        ]
        self._month_menu = MDDropdownMenu(
            caller=btn, items=items, width_mult=4, max_height=dp(350),
        )
        self._month_menu.open()

    def _select_month(self, month: int) -> None:
        self._selected_month = month
        self._month_btn.text = get_month_name(month)
        if self._month_menu:
            self._month_menu.dismiss()
        self._refresh()

    def _open_year_menu(self, btn) -> None:
        import datetime
        current_year = datetime.date.today().year
        years = list(range(current_year - 2, current_year + 3))
        items = [
            {
                "text": str(y),
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda y=y: self._select_year(y),
            }
            for y in years
        ]
        self._year_menu = MDDropdownMenu(
            caller=btn, items=items, width_mult=3, max_height=dp(280),
        )
        self._year_menu.open()

    def _select_year(self, year: int) -> None:
        self._selected_year = year
        self._year_btn.text = str(year)
        if self._year_menu:
            self._year_menu.dismiss()
        self._refresh()

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    @property
    def _month_str(self) -> str:
        return f"{self._selected_year}-{self._selected_month:02d}"

    def _load_summary(self) -> None:
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        fees = app.db.get_fees_by_month(self._month_str)
        summary = app.db.get_fee_summary_for_month(self._month_str)
        self._stat_labels["students"].text = str(len(fees))
        self._stat_labels["expected"].text = format_currency(summary["total_expected"])
        self._stat_labels["collected"].text = format_currency(summary["total_collected"])
        self._stat_labels["pending"].text = format_currency(summary["total_pending"])

    def _load_fee_list(self) -> None:
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        fees = app.db.get_fees_by_month(self._month_str)

        if self._status_filter != "All":
            fees = [f for f in fees if f.get("status") == self._status_filter]

        self._fee_list.clear_widgets()
        if not fees:
            self._fee_list.add_widget(MDLabel(
                text="No fee records for this month.",
                font_style="Body1",
                theme_text_color="Hint",
                halign="center",
                size_hint_y=None, height=dp(60),
            ))
            return

        for fee in fees:
            row = KAFeeRow(fee=fee, on_tap=self._open_fee_detail)
            self._fee_list.add_widget(row)

    # ------------------------------------------------------------------
    # Generate fees
    # ------------------------------------------------------------------

    def _generate_fees(self) -> None:
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        generated, skipped = app.db.generate_monthly_fees(
            self._selected_month, self._selected_year
        )
        show_info_dialog(
            "Fees Generated",
            f"Generated: {generated} new fee records.\n"
            f"Skipped: {skipped} (already existed).",
        )
        self._refresh()

    # ------------------------------------------------------------------
    # Status filter
    # ------------------------------------------------------------------

    def _set_status_filter(self, status: str) -> None:
        self._status_filter = status
        self._highlight_filter_btn(status)
        self._load_fee_list()

    def _highlight_filter_btn(self, active: str) -> None:
        for status, btn in self._filter_buttons.items():
            if status == active:
                btn.md_bg_color = [0.10, 0.14, 0.49, 0.15]
            else:
                btn.md_bg_color = [0, 0, 0, 0]

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _open_fee_detail(self, fee: dict) -> None:
        app = App.get_running_app()
        if app:
            app.selected_fee_student_id = fee.get("student_id")
            app.go_to_screen("fee_detail")

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()
