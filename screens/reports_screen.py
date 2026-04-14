"""
Reports screen for Khan'z Academy Mobile App.

Provides four report types: Monthly Income, Defaulters, Class-wise, and Student Directory.
All reports are saved as PDF files.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDRaisedButton, MDFlatButton  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.menu import MDDropdownMenu  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore

from libs.utils import get_current_month_year, get_month_name, format_month_year
from widgets.dialogs import show_error_dialog, show_success_dialog, show_loading_indicator, dismiss_loading_indicator
from widgets.navigation import BottomNavBar


# ---------------------------------------------------------------------------
# ReportsScreen
# ---------------------------------------------------------------------------

class ReportsScreen(MDScreen):
    """
    Report-generation hub: one card per report type with a shared month/year selector.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "reports"
        month, year = get_current_month_year()
        self._selected_month: int = month
        self._selected_year: int = year
        self._month_menu: MDDropdownMenu = None  # type: ignore[assignment]
        self._year_menu: MDDropdownMenu = None   # type: ignore[assignment]
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Reports",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(12), dp(10), dp(12), dp(20)],
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # ---- Month / year selector ----
        my_card = MDCard(
            radius=[dp(10)] * 4, elevation=2,
            padding=dp(12), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None, height=dp(90),
        )
        my_col = MDBoxLayout(orientation="vertical", spacing=dp(6))
        my_col.add_widget(MDLabel(
            text="Report Period",
            font_style="Subtitle2", bold=True,
            theme_text_color="Custom", text_color=[0.10, 0.14, 0.49, 1],
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
            size_hint_x=0.55, height=dp(40),
            on_release=self._open_month_menu,
        )
        self._year_btn = MDRaisedButton(
            text=str(self._selected_year),
            md_bg_color=[0.10, 0.14, 0.49, 0.1],
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=0.45, height=dp(40),
            on_release=self._open_year_menu,
        )
        picker_row.add_widget(self._month_btn)
        picker_row.add_widget(self._year_btn)
        my_col.add_widget(picker_row)
        my_card.add_widget(my_col)
        content.add_widget(my_card)

        # ---- Report cards ----
        report_cards_data = [
            {
                "icon": "📈",
                "title": "Monthly Income Report",
                "description": "Total expected, collected, and pending fees for the selected month.",
                "color": [0.23, 0.62, 0.27, 1],
                "action": self._generate_income_report,
            },
            {
                "icon": "⚠️",
                "title": "Defaulters Report",
                "description": "Students with unpaid or partial fees for the selected month.",
                "color": [0.96, 0.26, 0.21, 1],
                "action": self._generate_defaulters_report,
            },
            {
                "icon": "🏫",
                "title": "Class-wise Report",
                "description": "Student count and fee potential per class across all 12 classes.",
                "color": [0.46, 0.10, 0.75, 1],
                "action": self._generate_classwise_report,
            },
            {
                "icon": "📋",
                "title": "Student Directory",
                "description": "Complete list of all currently enrolled active students.",
                "color": [0.10, 0.45, 0.67, 1],
                "action": self._generate_directory_report,
            },
        ]
        for rcd in report_cards_data:
            content.add_widget(self._make_report_card(rcd))

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(BottomNavBar(active_screen="reports"))
        self.add_widget(root)

    def _make_report_card(self, rcd: dict) -> MDCard:
        """Build a single report-type card with a GENERATE button."""
        card = MDCard(
            radius=[dp(12)] * 4, elevation=2,
            padding=dp(14), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None, height=dp(120),
        )
        col = MDBoxLayout(orientation="vertical", spacing=dp(4))

        header_row = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(34),
        )
        header_row.add_widget(MDLabel(
            text=rcd["icon"],
            font_style="H5",
            size_hint_x=None, width=dp(36),
            halign="left",
        ))
        header_row.add_widget(MDLabel(
            text=rcd["title"],
            font_style="Subtitle1", bold=True,
            theme_text_color="Custom", text_color=rcd["color"],
        ))
        col.add_widget(header_row)

        col.add_widget(MDLabel(
            text=rcd["description"],
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None, height=dp(30),
        ))

        gen_btn = MDRaisedButton(
            text="GENERATE",
            md_bg_color=rcd["color"],
            size_hint_x=1, height=dp(36),
            on_release=lambda _b, fn=rcd["action"]: fn(),
        )
        col.add_widget(gen_btn)
        card.add_widget(col)
        return card

    # ------------------------------------------------------------------
    # Month / year pickers
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

    @property
    def _month_str(self) -> str:
        return f"{self._selected_year}-{self._selected_month:02d}"

    # ------------------------------------------------------------------
    # Report generators
    # ------------------------------------------------------------------

    def _generate_income_report(self) -> None:
        from libs.pdf_generator import ReportGenerator

        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        show_loading_indicator()
        try:
            fee_records = app.db.get_monthly_income_detailed(self._month_str)
            summary = app.db.get_fee_summary_for_month(self._month_str)
            gen = ReportGenerator()
            path = gen.generate_monthly_income_report(self._month_str, fee_records, summary)
            dismiss_loading_indicator()
            if path:
                show_success_dialog("Report Generated", f"Income report saved to:\n{path}")
            else:
                show_error_dialog("Report Failed", "Could not generate the income report.")
        except Exception as exc:
            dismiss_loading_indicator()
            from libs.utils import log_error
            log_error("ReportsScreen._generate_income_report failed", exc)
            show_error_dialog("Error", "An unexpected error occurred.")

    def _generate_defaulters_report(self) -> None:
        from libs.pdf_generator import ReportGenerator

        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        show_loading_indicator()
        try:
            defaulters = app.db.get_defaulters_report(self._month_str)
            gen = ReportGenerator()
            path = gen.generate_defaulters_report(self._month_str, defaulters)
            dismiss_loading_indicator()
            if path:
                show_success_dialog("Report Generated",
                                    f"Defaulters report saved to:\n{path}")
            else:
                show_error_dialog("Report Failed", "Could not generate the defaulters report.")
        except Exception as exc:
            dismiss_loading_indicator()
            from libs.utils import log_error
            log_error("ReportsScreen._generate_defaulters_report failed", exc)
            show_error_dialog("Error", "An unexpected error occurred.")

    def _generate_classwise_report(self) -> None:
        from libs.pdf_generator import ReportGenerator

        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        show_loading_indicator()
        try:
            class_data = app.db.get_class_wise_report()
            students_by_class = {}
            for cls in app.db.get_all_classes():
                students_by_class[cls["id"]] = app.db.get_students_in_class(cls["id"])
            gen = ReportGenerator()
            path = gen.generate_class_wise_report(class_data, students_by_class)
            dismiss_loading_indicator()
            if path:
                show_success_dialog("Report Generated",
                                    f"Class-wise report saved to:\n{path}")
            else:
                show_error_dialog("Report Failed", "Could not generate the class-wise report.")
        except Exception as exc:
            dismiss_loading_indicator()
            from libs.utils import log_error
            log_error("ReportsScreen._generate_classwise_report failed", exc)
            show_error_dialog("Error", "An unexpected error occurred.")

    def _generate_directory_report(self) -> None:
        from libs.pdf_generator import ReportGenerator

        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        show_loading_indicator()
        try:
            students = app.db.get_all_students(active_only=True)
            gen = ReportGenerator()
            path = gen.generate_student_directory(students)
            dismiss_loading_indicator()
            if path:
                show_success_dialog("Report Generated",
                                    f"Student directory saved to:\n{path}")
            else:
                show_error_dialog("Report Failed", "Could not generate the student directory.")
        except Exception as exc:
            dismiss_loading_indicator()
            from libs.utils import log_error
            log_error("ReportsScreen._generate_directory_report failed", exc)
            show_error_dialog("Error", "An unexpected error occurred.")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()
