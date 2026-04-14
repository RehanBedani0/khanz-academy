"""
Voucher screen for Khan'z Academy Mobile App.

Shows a searchable list of all generated vouchers and allows new voucher creation.
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
from kivymd.uix.textfield import MDTextField  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore
from kivymd.uix.button import MDRaisedButton  # type: ignore

from libs.utils import format_date, format_month_year
from widgets.dialogs import show_error_dialog, show_info_dialog
from widgets.navigation import BottomNavBar


class VoucherScreen(MDScreen):
    """
    Voucher management screen: list and search generated PDF vouchers.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "voucher"
        self._all_vouchers: list = []
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Fee Vouchers",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        # Search bar
        search_bar = MDBoxLayout(
            orientation="horizontal",
            padding=[dp(12), dp(6)],
            size_hint_y=None, height=dp(60),
        )
        self._search_field = MDTextField(
            hint_text="🔍  Search by student name or voucher number…",
            size_hint_x=1,
            on_text=self._on_search,
        )
        search_bar.add_widget(self._search_field)
        root.add_widget(search_bar)

        # Count label
        self._count_lbl = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None, height=dp(20),
            padding=[dp(14), 0],
        )
        root.add_widget(self._count_lbl)

        # Scrollable voucher list
        scroll = ScrollView()
        self._list_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=[dp(12), dp(4), dp(12), dp(80)],
            size_hint_y=None,
        )
        self._list_box.bind(minimum_height=self._list_box.setter("height"))
        scroll.add_widget(self._list_box)
        root.add_widget(scroll)

        root.add_widget(BottomNavBar(active_screen="voucher"))
        self.add_widget(root)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        Clock.schedule_once(lambda _dt: self._load_vouchers(), 0)

    def _load_vouchers(self) -> None:
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        self._all_vouchers = app.db.get_all_vouchers()
        self._apply_filter()

    def _apply_filter(self) -> None:
        query = self._search_field.text.strip().lower()
        if query:
            filtered = [
                v for v in self._all_vouchers
                if query in v.get("student_name", "").lower()
                or query in v.get("voucher_number", "").lower()
            ]
        else:
            filtered = list(self._all_vouchers)
        self._render_list(filtered)

    def _render_list(self, vouchers: list) -> None:
        self._list_box.clear_widgets()
        count = len(vouchers)
        self._count_lbl.text = f"{count} voucher{'s' if count != 1 else ''}"

        if not vouchers:
            self._list_box.add_widget(MDLabel(
                text="No vouchers generated yet.",
                font_style="Body1", theme_text_color="Hint",
                halign="center", size_hint_y=None, height=dp(80),
            ))
            return

        for voucher in vouchers:
            card = self._make_voucher_card(voucher)
            self._list_box.add_widget(card)

    def _make_voucher_card(self, voucher: dict) -> MDCard:
        """Build a single voucher list card."""
        card = MDCard(
            radius=[dp(10)] * 4, elevation=1,
            padding=dp(12), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None, height=dp(100),
            ripple_behavior=True,
        )
        col = MDBoxLayout(orientation="vertical", spacing=dp(4))

        # Voucher number + date
        top_row = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(26),
        )
        top_row.add_widget(MDLabel(
            text=voucher.get("voucher_number", ""),
            font_style="Subtitle2", bold=True,
            theme_text_color="Custom", text_color=[0.00, 0.51, 0.50, 1],
            size_hint_x=0.65,
        ))
        top_row.add_widget(MDLabel(
            text=format_date(voucher.get("generated_at", "")[:10]),
            font_style="Caption", theme_text_color="Secondary",
            size_hint_x=0.35, halign="right",
        ))
        col.add_widget(top_row)

        col.add_widget(MDLabel(
            text=voucher.get("student_name", ""),
            font_style="Body2",
            theme_text_color="Primary",
            size_hint_y=None, height=dp(22),
        ))

        bottom_row = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(20),
        )
        bottom_row.add_widget(MDLabel(
            text=voucher.get("class_name", ""),
            font_style="Caption", theme_text_color="Secondary",
            size_hint_x=0.35,
        ))
        bottom_row.add_widget(MDLabel(
            text=format_month_year(voucher.get("month", "")),
            font_style="Caption", theme_text_color="Secondary",
            size_hint_x=0.65, halign="right",
        ))
        col.add_widget(bottom_row)

        card.add_widget(col)

        # Tap → show file info
        file_path = voucher.get("file_path", "")
        card.bind(
            on_touch_up=lambda c, t, fp=file_path: self._on_voucher_tap(c, t, fp)
        )
        return card

    def _on_voucher_tap(self, card, touch, file_path: str) -> None:
        if not card.collide_point(*touch.pos):
            return
        if os.path.exists(file_path):
            show_info_dialog("Voucher File", f"Saved at:\n{file_path}")
        else:
            show_error_dialog("File Not Found",
                              f"The voucher file was not found at:\n{file_path}")

    def _on_search(self, _field, _text) -> None:
        self._apply_filter()

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()
