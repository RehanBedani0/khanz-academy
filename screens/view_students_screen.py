"""
View Students screen for Khan'z Academy Mobile App.

Shows a searchable, filterable list of all enrolled students.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.menu import MDDropdownMenu  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.textfield import MDTextField  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore
from kivy.uix.floatlayout import FloatLayout  # type: ignore

from widgets.custom_widgets import KAStudentCard
from widgets.navigation import BottomNavBar


# ---------------------------------------------------------------------------
# ViewStudentsScreen
# ---------------------------------------------------------------------------

class ViewStudentsScreen(MDScreen):
    """
    Scrollable student list with real-time search and class filter.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "view_students"
        self._all_students: list = []
        self._filter_class_id: int = None   # type: ignore[assignment]
        self._class_menu: MDDropdownMenu = None  # type: ignore[assignment]
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root_float = FloatLayout()

        main_col = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
        )

        # Top app bar
        toolbar = MDTopAppBar(
            title="Students",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        main_col.add_widget(toolbar)

        # Search + filter row
        filter_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            padding=[dp(12), dp(6), dp(12), dp(4)],
            size_hint_y=None,
            height=dp(60),
        )
        self._search_field = MDTextField(
            hint_text="🔍  Search by name…",
            size_hint_x=0.65,
            height=dp(48),
            on_text=self._on_search_change,
        )
        self._class_filter_btn = MDRaisedButton(
            text="All Classes",
            md_bg_color=[0.10, 0.14, 0.49, 0.15],
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=0.35,
            height=dp(40),
            on_release=self._open_class_filter_menu,
        )
        filter_row.add_widget(self._search_field)
        filter_row.add_widget(self._class_filter_btn)
        main_col.add_widget(filter_row)

        # Student count label
        self._count_lbl = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            padding=[dp(14), 0],
        )
        main_col.add_widget(self._count_lbl)

        # Scrollable list area
        scroll = ScrollView()
        self._list_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=[dp(12), dp(4), dp(12), dp(80)],
            size_hint_y=None,
        )
        self._list_box.bind(minimum_height=self._list_box.setter("height"))
        scroll.add_widget(self._list_box)
        main_col.add_widget(scroll)

        # Bottom nav
        main_col.add_widget(BottomNavBar(active_screen="view_students"))

        root_float.add_widget(main_col)

        # FAB
        fab = MDFloatingActionButton(
            icon="plus",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            pos_hint={"right": 0.96, "y": 0.10},
            on_release=lambda _b: self._go_add_student(),
        )
        root_float.add_widget(fab)
        self.add_widget(root_float)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        """Reload student list every time this screen is shown."""
        Clock.schedule_once(lambda _dt: self._load_students(), 0)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_students(self) -> None:
        """Fetch all active students from the database."""
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        self._all_students = app.db.get_all_students(active_only=True)
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Apply current search text and class filter, then re-render."""
        query = self._search_field.text.strip().lower()
        filtered = self._all_students

        if self._filter_class_id is not None:
            filtered = [s for s in filtered if s.get("class_id") == self._filter_class_id]

        if query:
            filtered = [s for s in filtered if query in s.get("student_name", "").lower()]

        self._render_list(filtered)

    def _render_list(self, students: list) -> None:
        """Clear and repopulate the list box with student cards."""
        self._list_box.clear_widgets()

        count = len(students)
        self._count_lbl.text = f"{count} student{'s' if count != 1 else ''} found"

        if not students:
            empty = MDLabel(
                text="No students found",
                font_style="Body1",
                theme_text_color="Hint",
                halign="center",
                size_hint_y=None,
                height=dp(80),
            )
            self._list_box.add_widget(empty)
            return

        for student in students:
            card = KAStudentCard(
                student=student,
                on_tap=self._open_student,
            )
            self._list_box.add_widget(card)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_search_change(self, field, text) -> None:
        """Called every time the search text changes."""
        self._apply_filters()

    def _open_class_filter_menu(self, btn) -> None:
        """Open the class filter dropdown."""
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        classes = app.db.get_all_classes()

        items = [
            {
                "text": "All Classes",
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda: self._set_class_filter(None, "All Classes"),
            }
        ]
        for cls in classes:
            items.append({
                "text": cls["class_name"],
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda c=cls: self._set_class_filter(c["id"], c["class_name"]),
            })

        self._class_menu = MDDropdownMenu(
            caller=btn,
            items=items,
            width_mult=4,
            max_height=dp(350),
        )
        self._class_menu.open()

    def _set_class_filter(self, class_id, class_name: str) -> None:
        """Apply or clear the class filter."""
        self._filter_class_id = class_id
        self._class_filter_btn.text = class_name
        if self._class_menu:
            self._class_menu.dismiss()
        self._apply_filters()

    def _open_student(self, student: dict) -> None:
        """Navigate to the Student Detail screen."""
        app = App.get_running_app()
        if app is None:
            return
        app.selected_student_id = student["id"]
        app.go_to_screen("student_detail")

    def _go_add_student(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_to_screen("add_student")

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()

    def filter_by_class(self, class_id: int, class_name: str) -> None:
        """Pre-apply a class filter (called from class management screen)."""
        self._filter_class_id = class_id
        self._class_filter_btn.text = class_name
        Clock.schedule_once(lambda _dt: self._load_students(), 0)
