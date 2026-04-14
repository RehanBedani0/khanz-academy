"""
Add Student screen for Khan'z Academy Mobile App.

A scrollable form for enrolling a new student with full field validation.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDFlatButton, MDRaisedButton  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.menu import MDDropdownMenu  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.textfield import MDTextField  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore
from kivymd.uix.button import MDRaisedButton  # type: ignore

from libs.utils import get_current_date
from libs.validators import (
    validate_student_name,
    validate_father_name,
    validate_phone_number,
    validate_address,
    validate_monthly_fee,
    validate_date,
    validate_class_selection,
)
from widgets.dialogs import show_error_dialog, show_success_dialog


# ---------------------------------------------------------------------------
# AddStudentScreen
# ---------------------------------------------------------------------------

class AddStudentScreen(MDScreen):
    """
    Form screen for adding a new student to the academy.

    All fields are validated before any database write is attempted.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "add_student"
        self._selected_class_id: int = None   # type: ignore[assignment]
        self._selected_class_name: str = ""
        self._class_menu: MDDropdownMenu = None  # type: ignore[assignment]
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = MDBoxLayout(orientation="vertical")

        # Top app bar
        toolbar = MDTopAppBar(
            title="Add New Student",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        root.add_widget(toolbar)

        # Scrollable form
        scroll = ScrollView()
        form = MDBoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(16), dp(16), dp(16), dp(24)],
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter("height"))

        # ---- Student Name ----
        self.f_student_name = MDTextField(
            hint_text="Student Name *",
            helper_text="Full name (letters and spaces only)",
            helper_text_mode="on_error",
            max_text_length=100,
            size_hint_y=None,
            height=dp(56),
        )
        form.add_widget(self.f_student_name)

        # ---- Father Name ----
        self.f_father_name = MDTextField(
            hint_text="Father Name *",
            helper_text="Father's full name",
            helper_text_mode="on_error",
            max_text_length=100,
            size_hint_y=None,
            height=dp(56),
        )
        form.add_widget(self.f_father_name)

        # ---- Class selector ----
        self.f_class_btn = MDRaisedButton(
            text="Select Class  ▼",
            md_bg_color=[0.95, 0.95, 0.95, 1],
            theme_text_color="Custom",
            text_color=[0.30, 0.30, 0.30, 1],
            size_hint_x=1,
            height=dp(48),
            on_release=self._open_class_menu,
        )
        form.add_widget(self.f_class_btn)
        self._class_error_lbl = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.96, 0.26, 0.21, 1],
            size_hint_y=None,
            height=dp(16),
        )
        form.add_widget(self._class_error_lbl)

        # ---- Phone Number ----
        self.f_phone = MDTextField(
            hint_text="Phone Number *",
            helper_text="10-15 digits",
            helper_text_mode="on_error",
            input_filter="int",
            max_text_length=15,
            size_hint_y=None,
            height=dp(56),
        )
        form.add_widget(self.f_phone)

        # ---- Address ----
        self.f_address = MDTextField(
            hint_text="Address (optional)",
            helper_text="Home or permanent address",
            helper_text_mode="on_focus",
            multiline=True,
            max_text_length=200,
            size_hint_y=None,
            height=dp(80),
        )
        form.add_widget(self.f_address)

        # ---- Admission Date ----
        self.f_admission_date = MDTextField(
            hint_text="Admission Date *",
            helper_text="Format: YYYY-MM-DD",
            helper_text_mode="on_error",
            text=get_current_date(),
            max_text_length=10,
            size_hint_y=None,
            height=dp(56),
        )
        form.add_widget(self.f_admission_date)

        # ---- Monthly Fee ----
        self.f_monthly_fee = MDTextField(
            hint_text="Monthly Fee (Rs.) *",
            helper_text="Positive number e.g. 1500",
            helper_text_mode="on_error",
            input_filter="float",
            size_hint_y=None,
            height=dp(56),
        )
        form.add_widget(self.f_monthly_fee)

        # ---- Buttons ----
        btn_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(52),
        )
        clear_btn = MDFlatButton(
            text="CLEAR",
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=0.35,
            on_release=lambda _b: self._clear_form(),
        )
        save_btn = MDRaisedButton(
            text="SAVE STUDENT",
            md_bg_color=[0.23, 0.62, 0.27, 1],
            size_hint_x=0.65,
            height=dp(48),
            on_release=lambda _b: self._save_student(),
        )
        btn_row.add_widget(clear_btn)
        btn_row.add_widget(save_btn)
        form.add_widget(btn_row)

        scroll.add_widget(form)
        root.add_widget(scroll)
        self.add_widget(root)

    # ------------------------------------------------------------------
    # Class dropdown
    # ------------------------------------------------------------------

    def _open_class_menu(self, btn) -> None:
        """Build and open the class selection dropdown."""
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        classes = app.db.get_all_classes()
        if not classes:
            show_error_dialog("Error", "No classes found in database.")
            return

        menu_items = [
            {
                "text": cls["class_name"],
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda x=cls: self._select_class(x),
            }
            for cls in classes
        ]
        self._class_menu = MDDropdownMenu(
            caller=btn,
            items=menu_items,
            width_mult=4,
            max_height=dp(300),
        )
        self._class_menu.open()

    def _select_class(self, cls: dict) -> None:
        """Store the selected class and update the button label."""
        self._selected_class_id = cls["id"]
        self._selected_class_name = cls["class_name"]
        self.f_class_btn.text = cls["class_name"]
        self.f_class_btn.md_bg_color = [0.10, 0.14, 0.49, 0.1]
        self.f_class_btn.theme_text_color = "Custom"
        self.f_class_btn.text_color = [0.10, 0.14, 0.49, 1]
        self._class_error_lbl.text = ""
        if self._class_menu:
            self._class_menu.dismiss()

    # ------------------------------------------------------------------
    # Validation & save
    # ------------------------------------------------------------------

    def _save_student(self) -> None:
        """Validate all fields and save the student if valid."""
        errors = []

        # Student name
        valid, msg = validate_student_name(self.f_student_name.text)
        if not valid:
            self.f_student_name.error = True
            self.f_student_name.helper_text = msg
            errors.append(msg)
        else:
            self.f_student_name.error = False

        # Father name
        valid, msg = validate_father_name(self.f_father_name.text)
        if not valid:
            self.f_father_name.error = True
            self.f_father_name.helper_text = msg
            errors.append(msg)
        else:
            self.f_father_name.error = False

        # Class
        valid, msg = validate_class_selection(self._selected_class_id)
        if not valid:
            self._class_error_lbl.text = msg
            errors.append(msg)
        else:
            self._class_error_lbl.text = ""

        # Phone
        valid, msg = validate_phone_number(self.f_phone.text)
        if not valid:
            self.f_phone.error = True
            self.f_phone.helper_text = msg
            errors.append(msg)
        else:
            self.f_phone.error = False

        # Address (optional)
        valid, msg = validate_address(self.f_address.text)
        if not valid:
            self.f_address.error = True
            self.f_address.helper_text = msg
            errors.append(msg)
        else:
            self.f_address.error = False

        # Admission date
        valid, msg = validate_date(self.f_admission_date.text)
        if not valid:
            self.f_admission_date.error = True
            self.f_admission_date.helper_text = msg
            errors.append(msg)
        else:
            self.f_admission_date.error = False

        # Monthly fee
        valid, msg = validate_monthly_fee(self.f_monthly_fee.text)
        if not valid:
            self.f_monthly_fee.error = True
            self.f_monthly_fee.helper_text = msg
            errors.append(msg)
        else:
            self.f_monthly_fee.error = False

        if errors:
            show_error_dialog("Validation Error", errors[0])
            return

        # All valid — persist
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            show_error_dialog("Error", "Database not available.")
            return

        student_id = app.db.add_student(
            student_name=self.f_student_name.text.strip(),
            father_name=self.f_father_name.text.strip(),
            class_id=int(self._selected_class_id),
            phone_number=self.f_phone.text.strip(),
            address=self.f_address.text.strip(),
            admission_date=self.f_admission_date.text.strip(),
            monthly_fee=float(self.f_monthly_fee.text.strip()),
        )
        if student_id:
            show_success_dialog(
                "Student Added",
                f"{self.f_student_name.text.strip()} has been enrolled successfully!",
            )
            self._clear_form()
        else:
            show_error_dialog("Save Failed", "Could not save the student. Please try again.")

    def _clear_form(self) -> None:
        """Reset all form fields to their default state."""
        self.f_student_name.text = ""
        self.f_student_name.error = False
        self.f_father_name.text = ""
        self.f_father_name.error = False
        self.f_phone.text = ""
        self.f_phone.error = False
        self.f_address.text = ""
        self.f_address.error = False
        self.f_admission_date.text = get_current_date()
        self.f_admission_date.error = False
        self.f_monthly_fee.text = ""
        self.f_monthly_fee.error = False
        self._selected_class_id = None
        self._selected_class_name = ""
        self.f_class_btn.text = "Select Class  ▼"
        self.f_class_btn.md_bg_color = [0.95, 0.95, 0.95, 1]
        self.f_class_btn.text_color = [0.30, 0.30, 0.30, 1]
        self._class_error_lbl.text = ""

    def _go_back(self) -> None:
        """Navigate back to the previous screen."""
        app = App.get_running_app()
        if app:
            app.go_back()
