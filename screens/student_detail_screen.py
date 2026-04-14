"""
Student Detail screen for Khan'z Academy Mobile App.

Shows all fields for a single student with Edit / Delete / Fees / Voucher actions.
"""

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDFlatButton, MDRaisedButton  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.menu import MDDropdownMenu  # type: ignore
from kivymd.uix.screen import MDScreen  # type: ignore
from kivymd.uix.textfield import MDTextField  # type: ignore
from kivymd.uix.toolbar import MDTopAppBar  # type: ignore

from libs.utils import format_currency, format_date, get_current_date
from libs.validators import (
    validate_student_name, validate_father_name, validate_phone_number,
    validate_address, validate_monthly_fee, validate_date, validate_class_selection,
)
from widgets.dialogs import (
    show_error_dialog, show_success_dialog, show_confirmation_dialog,
)


# ---------------------------------------------------------------------------
# StudentDetailScreen
# ---------------------------------------------------------------------------

class StudentDetailScreen(MDScreen):
    """
    Detailed view for a single student with view/edit modes.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "student_detail"
        self._student_id: int = None   # type: ignore[assignment]
        self._student: dict = {}
        self._edit_mode: bool = False
        self._selected_class_id: int = None  # type: ignore[assignment]
        self._class_menu: MDDropdownMenu = None  # type: ignore[assignment]
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._root_col = MDBoxLayout(orientation="vertical")

        # Toolbar (title set dynamically)
        self._toolbar = MDTopAppBar(
            title="Student Detail",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        self._root_col.add_widget(self._toolbar)

        self._scroll = ScrollView()
        self._content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(14), dp(10), dp(14), dp(24)],
            size_hint_y=None,
        )
        self._content.bind(minimum_height=self._content.setter("height"))
        self._scroll.add_widget(self._content)
        self._root_col.add_widget(self._scroll)
        self.add_widget(self._root_col)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        """Load the selected student whenever the screen appears."""
        app = App.get_running_app()
        if app and hasattr(app, "selected_student_id") and app.selected_student_id:
            self._student_id = app.selected_student_id
            Clock.schedule_once(lambda _dt: self._load_student(), 0)

    def _load_student(self) -> None:
        """Fetch student data and rebuild the content area."""
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        self._student = app.db.get_student(self._student_id) or {}
        self._toolbar.title = self._student.get("student_name", "Student Detail")
        self._selected_class_id = self._student.get("class_id")
        self._render_view_mode()

    # ------------------------------------------------------------------
    # View mode
    # ------------------------------------------------------------------

    def _render_view_mode(self) -> None:
        """Populate the content area with student info in read-only mode."""
        self._edit_mode = False
        self._content.clear_widgets()
        s = self._student

        # Info card
        info_card = MDCard(
            radius=[dp(12)] * 4,
            elevation=2,
            padding=dp(14),
            md_bg_color=[1, 1, 1, 1],
            size_hint_y=None,
        )
        info_col = MDBoxLayout(orientation="vertical", spacing=dp(6),
                               size_hint_y=None)
        info_col.bind(minimum_height=info_col.setter("height"))

        rows = [
            ("Student Name",   s.get("student_name", "")),
            ("Father Name",    s.get("father_name", "")),
            ("Class",          s.get("class_name", "")),
            ("Phone",          s.get("phone_number", "")),
            ("Address",        s.get("address", "") or "—"),
            ("Admission Date", format_date(s.get("admission_date", ""))),
            ("Monthly Fee",    format_currency(s.get("monthly_fee", 0))),
            ("Status",         "Active" if s.get("is_active", 1) else "Inactive"),
        ]
        for label, value in rows:
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(28),
            )
            row.add_widget(MDLabel(
                text=f"[b]{label}[/b]",
                markup=True,
                font_style="Body2",
                size_hint_x=0.40,
                theme_text_color="Secondary",
            ))
            row.add_widget(MDLabel(
                text=str(value),
                font_style="Body2",
                theme_text_color="Primary",
                size_hint_x=0.60,
            ))
            info_col.add_widget(row)
        info_card.add_widget(info_col)
        self._content.add_widget(info_card)

        # Fee summary card
        fee_summary = self._build_fee_summary()
        self._content.add_widget(fee_summary)

        # Action buttons
        actions = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(220),
        )
        edit_btn = MDRaisedButton(
            text="✏️  EDIT STUDENT",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=1,
            height=dp(48),
            on_release=lambda _b: self._render_edit_mode(),
        )
        fees_btn = MDRaisedButton(
            text="💳  VIEW FEES",
            md_bg_color=[0.80, 0.51, 0.01, 1],
            size_hint_x=1,
            height=dp(48),
            on_release=lambda _b: self._go_to_fees(),
        )
        voucher_btn = MDRaisedButton(
            text="🧾  GENERATE VOUCHER",
            md_bg_color=[0.00, 0.51, 0.50, 1],
            size_hint_x=1,
            height=dp(48),
            on_release=lambda _b: self._generate_latest_voucher(),
        )
        delete_btn = MDRaisedButton(
            text="🗑️  DELETE STUDENT",
            md_bg_color=[0.96, 0.26, 0.21, 1],
            size_hint_x=1,
            height=dp(48),
            on_release=lambda _b: self._confirm_delete(),
        )
        actions.add_widget(edit_btn)
        actions.add_widget(fees_btn)
        actions.add_widget(voucher_btn)
        actions.add_widget(delete_btn)
        self._content.add_widget(actions)

    def _build_fee_summary(self) -> MDCard:
        """Return a card summarising this student's fee totals."""
        app = App.get_running_app()
        total_expected = 0.0
        total_paid = 0.0
        if app and hasattr(app, "db"):
            fees = app.db.get_fees_by_student(self._student_id)
            for fee in fees:
                total_expected += float(fee.get("fee_amount", 0))
                total_paid += float(fee.get("paid_amount", 0))
        outstanding = max(0.0, total_expected - total_paid)

        card = MDCard(
            radius=[dp(12)] * 4,
            elevation=2,
            padding=dp(14),
            md_bg_color=[1, 1, 1, 1],
            size_hint_y=None,
        )
        col = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        col.bind(minimum_height=col.setter("height"))

        col.add_widget(MDLabel(
            text="[b]Fee Summary[/b]",
            markup=True,
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_y=None,
            height=dp(26),
        ))
        for label, value, color in [
            ("Total Fees Due",  format_currency(total_expected),  [0.13, 0.13, 0.13, 1]),
            ("Total Paid",      format_currency(total_paid),      [0.23, 0.62, 0.27, 1]),
            ("Outstanding",     format_currency(outstanding),      [0.96, 0.26, 0.21, 1]),
        ]:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
            row.add_widget(MDLabel(text=label, font_style="Body2",
                                   theme_text_color="Secondary", size_hint_x=0.50))
            row.add_widget(MDLabel(text=value, font_style="Body2",
                                   theme_text_color="Custom", text_color=color,
                                   bold=True, size_hint_x=0.50, halign="right"))
            col.add_widget(row)
        card.add_widget(col)
        return card

    # ------------------------------------------------------------------
    # Edit mode
    # ------------------------------------------------------------------

    def _render_edit_mode(self) -> None:
        """Switch content area to an editable form pre-filled with student data."""
        self._edit_mode = True
        self._content.clear_widgets()
        s = self._student

        def _field(hint, text="", helper="", multiline=False, input_filter=None):
            kwargs = dict(
                hint_text=hint, text=str(text),
                helper_text=helper, helper_text_mode="on_error",
                size_hint_y=None, height=dp(80 if multiline else 56),
                multiline=multiline,
            )
            if input_filter:
                kwargs["input_filter"] = input_filter
            return MDTextField(**kwargs)

        self._e_name = _field("Student Name *", s.get("student_name", ""))
        self._e_father = _field("Father Name *", s.get("father_name", ""))
        self._e_phone = _field("Phone Number *", s.get("phone_number", ""),
                               input_filter="int")
        self._e_address = _field("Address", s.get("address", ""), multiline=True)
        self._e_date = _field("Admission Date *", s.get("admission_date", ""),
                              helper="YYYY-MM-DD")
        self._e_fee = _field("Monthly Fee (Rs.) *",
                             str(s.get("monthly_fee", "")),
                             input_filter="float")

        # Class selector button
        self._e_class_btn = MDRaisedButton(
            text=s.get("class_name", "Select Class  ▼"),
            md_bg_color=[0.10, 0.14, 0.49, 0.1],
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=1,
            height=dp(48),
            on_release=self._open_edit_class_menu,
        )
        self._e_class_err = MDLabel(
            text="", font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.96, 0.26, 0.21, 1],
            size_hint_y=None, height=dp(16),
        )

        for widget in [
            self._e_name, self._e_father, self._e_class_btn,
            self._e_class_err, self._e_phone, self._e_address,
            self._e_date, self._e_fee,
        ]:
            self._content.add_widget(widget)

        # Save / Cancel
        btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                              size_hint_y=None, height=dp(52))
        cancel_btn = MDFlatButton(
            text="CANCEL",
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=0.35,
            on_release=lambda _b: self._render_view_mode(),
        )
        save_btn = MDRaisedButton(
            text="SAVE CHANGES",
            md_bg_color=[0.23, 0.62, 0.27, 1],
            size_hint_x=0.65,
            height=dp(48),
            on_release=lambda _b: self._save_edits(),
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        self._content.add_widget(btn_row)

    def _open_edit_class_menu(self, btn) -> None:
        app = App.get_running_app()
        if app is None:
            return
        classes = app.db.get_all_classes()
        items = [
            {
                "text": cls["class_name"],
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda c=cls: self._set_edit_class(c),
            }
            for cls in classes
        ]
        self._class_menu = MDDropdownMenu(caller=btn, items=items,
                                          width_mult=4, max_height=dp(300))
        self._class_menu.open()

    def _set_edit_class(self, cls: dict) -> None:
        self._selected_class_id = cls["id"]
        self._e_class_btn.text = cls["class_name"]
        self._e_class_err.text = ""
        if self._class_menu:
            self._class_menu.dismiss()

    def _save_edits(self) -> None:
        """Validate and persist edited student data."""
        errors = []

        def _chk(field, validator, *args):
            valid, msg = validator(field.text, *args)
            field.error = not valid
            if not valid:
                field.helper_text = msg
                errors.append(msg)
            return valid

        _chk(self._e_name, validate_student_name)
        _chk(self._e_father, validate_father_name)
        _chk(self._e_phone, validate_phone_number)
        _chk(self._e_date, validate_date)
        _chk(self._e_fee, validate_monthly_fee)
        validate_address(self._e_address.text)  # optional

        valid_cls, cls_msg = validate_class_selection(self._selected_class_id)
        if not valid_cls:
            self._e_class_err.text = cls_msg
            errors.append(cls_msg)
        else:
            self._e_class_err.text = ""

        if errors:
            show_error_dialog("Validation Error", errors[0])
            return

        app = App.get_running_app()
        if app is None:
            return
        ok = app.db.update_student(
            self._student_id,
            student_name=self._e_name.text.strip(),
            father_name=self._e_father.text.strip(),
            class_id=int(self._selected_class_id),
            phone_number=self._e_phone.text.strip(),
            address=self._e_address.text.strip(),
            admission_date=self._e_date.text.strip(),
            monthly_fee=float(self._e_fee.text.strip()),
        )
        if ok:
            show_success_dialog("Updated", "Student information saved successfully.")
            self._load_student()
        else:
            show_error_dialog("Save Failed", "Could not update student. Please try again.")

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def _confirm_delete(self) -> None:
        name = self._student.get("student_name", "this student")
        show_confirmation_dialog(
            "Delete Student",
            f"Are you sure you want to delete {name}? This action cannot be undone.",
            on_confirm_callback=self._do_delete,
        )

    def _do_delete(self) -> None:
        app = App.get_running_app()
        if app is None:
            return
        ok = app.db.delete_student(self._student_id)
        if ok:
            show_success_dialog("Deleted", "Student has been removed.")
            Clock.schedule_once(lambda _dt: self._go_back(), 1.5)
        else:
            show_error_dialog("Delete Failed", "Could not delete student.")

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def _go_to_fees(self) -> None:
        app = App.get_running_app()
        if app:
            app.selected_fee_student_id = self._student_id
            app.go_to_screen("fee_detail")

    def _generate_latest_voucher(self) -> None:
        """Generate a PDF voucher for the latest unpaid fee of this student."""
        from libs.pdf_generator import VoucherGenerator
        from libs.utils import get_vouchers_path, generate_filename, format_month_year
        import os

        app = App.get_running_app()
        if app is None:
            return
        fees = app.db.get_fees_by_student(self._student_id)
        unpaid = [f for f in fees if f.get("status") != "Paid"]
        if not unpaid:
            show_error_dialog("No Unpaid Fee",
                              "This student has no outstanding fee to generate a voucher for.")
            return
        fee = unpaid[0]
        voucher_number = app.db.generate_voucher_number()
        student_data = self._student
        filename = generate_filename(f"Voucher_{self._student_id}", "pdf")
        output_path = os.path.join(get_vouchers_path(), filename)

        gen = VoucherGenerator()
        path = gen.generate_fee_voucher(
            student_data=student_data,
            fee_data=fee,
            voucher_number=voucher_number,
            output_path=output_path,
        )
        if path:
            app.db.save_voucher_record(fee["id"], self._student_id, voucher_number, path)
            show_success_dialog("Voucher Generated",
                                f"Voucher saved to:\n{path}")
        else:
            show_error_dialog("Voucher Failed", "Could not generate the voucher PDF.")

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()
