"""
Class Management screen for Khan'z Academy Mobile App.

Displays a grid of all 12 class cards with live student counts.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.gridlayout import MDGridLayout  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore

from libs.utils import format_currency
from widgets.navigation import BottomNavBar


# Colour cycle for class cards
_CLASS_COLORS = [
    [0.10, 0.14, 0.49, 1],
    [0.23, 0.62, 0.27, 1],
    [0.80, 0.51, 0.01, 1],
    [0.62, 0.04, 0.23, 1],
    [0.00, 0.51, 0.50, 1],
    [0.46, 0.10, 0.75, 1],
    [0.10, 0.45, 0.67, 1],
    [0.33, 0.33, 0.33, 1],
    [0.55, 0.13, 0.00, 1],
    [0.00, 0.40, 0.25, 1],
    [0.40, 0.25, 0.00, 1],
    [0.25, 0.00, 0.40, 1],
]


class ClassManagementScreen(MDScreen):
    """
    Grid screen showing all 12 classes with live student counts.
    Tapping a class navigates to the filtered student list.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "class_management"
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Class Management",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        self._grid = MDGridLayout(
            cols=2,
            spacing=dp(10),
            padding=[dp(12), dp(10), dp(12), dp(20)],
            size_hint_y=None,
        )
        self._grid.bind(minimum_height=self._grid.setter("height"))
        scroll.add_widget(self._grid)
        root.add_widget(scroll)

        root.add_widget(BottomNavBar(active_screen="class_management"))
        self.add_widget(root)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        Clock.schedule_once(lambda _dt: self._load_classes(), 0)

    def _load_classes(self) -> None:
        """Fetch classes and student counts, then render cards."""
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        classes = app.db.get_all_classes()
        self._grid.clear_widgets()

        for idx, cls in enumerate(classes):
            class_id = cls["id"]
            student_count = app.db.get_student_count_by_class(class_id)
            # Total monthly fee potential
            students_in_class = app.db.get_students_in_class(class_id)
            total_fee = sum(float(s.get("monthly_fee", 0)) for s in students_in_class)
            color = _CLASS_COLORS[idx % len(_CLASS_COLORS)]
            card = self._make_class_card(cls, student_count, total_fee, color)
            self._grid.add_widget(card)

    def _make_class_card(
        self, cls: dict, student_count: int, total_fee: float, color: list
    ) -> MDCard:
        """Return a styled class card widget."""
        card = MDCard(
            radius=[dp(14)] * 4,
            elevation=3,
            padding=dp(14),
            size_hint_y=None,
            height=dp(110),
            ripple_behavior=True,
            md_bg_color=[1, 1, 1, 1],
        )
        inner = MDBoxLayout(orientation="vertical", spacing=dp(4))

        # Class name (coloured)
        name_lbl = MDLabel(
            text=cls["class_name"],
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=color,
            size_hint_y=None,
            height=dp(30),
        )
        # Student count
        count_lbl = MDLabel(
            text=f"👥 {student_count} student{'s' if student_count != 1 else ''}",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(22),
        )
        # Fee potential
        fee_lbl = MDLabel(
            text=f"💰 {format_currency(total_fee)}/mo",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.23, 0.62, 0.27, 1],
            size_hint_y=None,
            height=dp(20),
        )
        inner.add_widget(name_lbl)
        inner.add_widget(count_lbl)
        inner.add_widget(fee_lbl)
        card.add_widget(inner)

        # Bind tap → view_students filtered
        cid = cls["id"]
        cname = cls["class_name"]
        card.bind(
            on_touch_up=lambda c, t, ci=cid, cn=cname: self._open_class(c, t, ci, cn)
        )
        return card

    def _open_class(self, card, touch, class_id: int, class_name: str) -> None:
        if not card.collide_point(*touch.pos):
            return
        app = App.get_running_app()
        if app is None:
            return
        # Pre-set filter on the view_students screen
        vs_screen = app.root.get_screen("view_students")
        vs_screen.filter_by_class(class_id, class_name)
        app.go_to_screen("view_students")

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()
