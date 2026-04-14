"""
Fee Detail screen for Khan'z Academy Mobile App.

Shows complete fee history for a single student with payment recording
and voucher generation.
"""

import os

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

from libs.utils import (
    format_currency, format_date, format_month_year,
    get_current_date, get_vouchers_path, generate_filename,
)
from libs.validators import validate_payment_amount, validate_date
from widgets.dialogs import show_error_dialog, show_success_dialog
from widgets.custom_widgets import STATUS_COLORS


# Payment method options
PAYMENT_METHODS = ["Cash", "Bank Transfer", "Online", "Other"]


class FeeDetailScreen(MDScreen):
    """
    Per-student fee history with payment recording and voucher generation.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "fee_detail"
        self._student_id: int = None  # type: ignore[assignment]
        self._student: dict = {}
        self._fees: list = []
        self._selected_fee: dict = {}
        self._payment_method: str = "Cash"
        self._method_menu: MDDropdownMenu = None  # type: ignore[assignment]
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._root = MDBoxLayout(orientation="vertical")

        self._toolbar = MDTopAppBar(
            title="Fee Detail",
            md_bg_color=[0.10, 0.14, 0.49, 1],
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda _x: self._go_back()]],
            elevation=4,
        )
        self._root.add_widget(self._toolbar)

        self._scroll = ScrollView()
        self._content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(12), dp(10), dp(12), dp(24)],
            size_hint_y=None,
        )
        self._content.bind(minimum_height=self._content.setter("height"))
        self._scroll.add_widget(self._content)
        self._root.add_widget(self._scroll)
        self.add_widget(self._root)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self, *_args) -> None:
        app = App.get_running_app()
        if app and hasattr(app, "selected_fee_student_id") and app.selected_fee_student_id:
            self._student_id = app.selected_fee_student_id
            Clock.schedule_once(lambda _dt: self._load_data(), 0)

    def _load_data(self) -> None:
        app = App.get_running_app()
        if app is None or not hasattr(app, "db"):
            return
        self._student = app.db.get_student(self._student_id) or {}
        self._fees = app.db.get_fees_by_student(self._student_id)
        self._toolbar.title = self._student.get("student_name", "Fee Detail")
        self._render_content()

    def _render_content(self) -> None:
        """Rebuild the entire content area."""
        self._content.clear_widgets()

        # Student summary card
        self._content.add_widget(self._build_student_summary())

        # Fee history
        self._content.add_widget(MDLabel(
            text="[b]Fee History[/b]",
            markup=True, font_style="Subtitle1",
            theme_text_color="Custom", text_color=[0.10, 0.14, 0.49, 1],
            size_hint_y=None, height=dp(28),
        ))

        if not self._fees:
            self._content.add_widget(MDLabel(
                text="No fee records found for this student.",
                font_style="Body1", theme_text_color="Hint",
                halign="center", size_hint_y=None, height=dp(50),
            ))
        else:
            for fee in self._fees:
                self._content.add_widget(self._build_fee_row(fee))

    # ------------------------------------------------------------------
    # Widget builders
    # ------------------------------------------------------------------

    def _build_student_summary(self) -> MDCard:
        card = MDCard(
            radius=[dp(10)] * 4, elevation=2,
            padding=dp(12), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None,
        )
        col = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        col.bind(minimum_height=col.setter("height"))

        s = self._student
        for label, value in [
            ("Name",  s.get("student_name", "")),
            ("Class", s.get("class_name", "")),
            ("Phone", s.get("phone_number", "")),
        ]:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
            row.add_widget(MDLabel(
                text=f"[b]{label}[/b]", markup=True,
                font_style="Caption", theme_text_color="Secondary",
                size_hint_x=0.30,
            ))
            row.add_widget(MDLabel(
                text=str(value), font_style="Body2",
                theme_text_color="Primary", size_hint_x=0.70,
            ))
            col.add_widget(row)
        card.add_widget(col)
        return card

    def _build_fee_row(self, fee: dict) -> MDCard:
        """Build an expandable fee record card."""
        status = fee.get("status", "Unpaid")
        status_color = STATUS_COLORS.get(status, [0.13, 0.13, 0.13, 1])
        fee_amount = float(fee.get("fee_amount", 0))
        paid_amount = float(fee.get("paid_amount", 0))
        balance = max(0.0, fee_amount - paid_amount)
        month_label = format_month_year(fee.get("month", ""))

        card = MDCard(
            radius=[dp(10)] * 4, elevation=1,
            padding=dp(12), md_bg_color=[1, 1, 1, 1],
            size_hint_y=None,
        )
        col = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
        col.bind(minimum_height=col.setter("height"))

        # Header row: month + status badge
        header = MDBoxLayout(orientation="horizontal",
                             size_hint_y=None, height=dp(26))
        header.add_widget(MDLabel(
            text=month_label, font_style="Subtitle2",
            bold=True, theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1], size_hint_x=0.60,
        ))
        header.add_widget(MDLabel(
            text=status, font_style="Body2",
            bold=True, theme_text_color="Custom",
            text_color=status_color, size_hint_x=0.40, halign="right",
        ))
        col.add_widget(header)

        # Amounts row
        amounts = MDBoxLayout(orientation="horizontal",
                              size_hint_y=None, height=dp(22))
        amounts.add_widget(MDLabel(
            text=f"Fee: {format_currency(fee_amount)}",
            font_style="Caption", theme_text_color="Secondary", size_hint_x=0.34,
        ))
        amounts.add_widget(MDLabel(
            text=f"Paid: {format_currency(paid_amount)}",
            font_style="Caption", theme_text_color="Custom",
            text_color=[0.23, 0.62, 0.27, 1], size_hint_x=0.33,
        ))
        amounts.add_widget(MDLabel(
            text=f"Due: {format_currency(balance)}",
            font_style="Caption", theme_text_color="Custom",
            text_color=[0.96, 0.26, 0.21, 1] if balance > 0 else [0.23, 0.62, 0.27, 1],
            size_hint_x=0.33, halign="right",
        ))
        col.add_widget(amounts)

        # Action buttons
        if status != "Paid":
            btn_row = MDBoxLayout(orientation="horizontal",
                                  spacing=dp(6), size_hint_y=None, height=dp(40))
            pay_btn = MDRaisedButton(
                text="RECORD PAYMENT",
                md_bg_color=[0.23, 0.62, 0.27, 1],
                size_hint_x=0.55, height=dp(36),
                on_release=lambda _b, f=fee: self._show_payment_form(f),
            )
            voucher_btn = MDFlatButton(
                text="VOUCHER",
                theme_text_color="Custom",
                text_color=[0.00, 0.51, 0.50, 1],
                size_hint_x=0.45, height=dp(36),
                on_release=lambda _b, f=fee: self._generate_voucher(f),
            )
            btn_row.add_widget(pay_btn)
            btn_row.add_widget(voucher_btn)
            col.add_widget(btn_row)
        else:
            voucher_only = MDBoxLayout(orientation="horizontal",
                                       size_hint_y=None, height=dp(40))
            vb = MDFlatButton(
                text="VIEW / GENERATE VOUCHER",
                theme_text_color="Custom",
                text_color=[0.00, 0.51, 0.50, 1],
                size_hint_x=1, height=dp(36),
                on_release=lambda _b, f=fee: self._generate_voucher(f),
            )
            voucher_only.add_widget(vb)
            col.add_widget(voucher_only)

        # Payment history for this fee
        app = App.get_running_app()
        if app and hasattr(app, "db"):
            payments = app.db.get_payments_by_fee(fee["id"])
            if payments:
                col.add_widget(MDLabel(
                    text="[b]Payments:[/b]", markup=True,
                    font_style="Caption", theme_text_color="Secondary",
                    size_hint_y=None, height=dp(18),
                ))
                for pmt in payments:
                    pmt_row = MDBoxLayout(
                        orientation="horizontal",
                        size_hint_y=None, height=dp(18),
                    )
                    pmt_row.add_widget(MDLabel(
                        text=format_date(pmt.get("payment_date", "")),
                        font_style="Caption", theme_text_color="Secondary",
                        size_hint_x=0.28,
                    ))
                    pmt_row.add_widget(MDLabel(
                        text=format_currency(pmt.get("amount_paid", 0)),
                        font_style="Caption", theme_text_color="Custom",
                        text_color=[0.23, 0.62, 0.27, 1], size_hint_x=0.28,
                    ))
                    pmt_row.add_widget(MDLabel(
                        text=pmt.get("payment_method", ""),
                        font_style="Caption", theme_text_color="Hint",
                        size_hint_x=0.22,
                    ))
                    pmt_row.add_widget(MDLabel(
                        text=pmt.get("notes", ""),
                        font_style="Caption", theme_text_color="Hint",
                        size_hint_x=0.22,
                    ))
                    col.add_widget(pmt_row)

        card.add_widget(col)
        return card

    # ------------------------------------------------------------------
    # Payment form
    # ------------------------------------------------------------------

    def _show_payment_form(self, fee: dict) -> None:
        """Add an inline payment form below the selected fee card."""
        self._selected_fee = fee
        fee_amount = float(fee.get("fee_amount", 0))
        paid_amount = float(fee.get("paid_amount", 0))
        remaining = max(0.0, fee_amount - paid_amount)

        # Build a payment form card
        form_card = MDCard(
            radius=[dp(10)] * 4, elevation=3,
            padding=dp(14), md_bg_color=[0.97, 0.97, 1.0, 1],
            size_hint_y=None,
        )
        form_col = MDBoxLayout(orientation="vertical", spacing=dp(8),
                               size_hint_y=None)
        form_col.bind(minimum_height=form_col.setter("height"))

        form_col.add_widget(MDLabel(
            text=f"[b]Record Payment — Remaining: {format_currency(remaining)}[/b]",
            markup=True, font_style="Subtitle2",
            theme_text_color="Custom", text_color=[0.10, 0.14, 0.49, 1],
            size_hint_y=None, height=dp(24),
        ))

        self._pmt_amount = MDTextField(
            hint_text="Amount (Rs.) *",
            helper_text=f"Max: Rs. {remaining:,.2f}",
            helper_text_mode="on_focus",
            input_filter="float",
            size_hint_y=None, height=dp(56),
        )
        self._pmt_date = MDTextField(
            hint_text="Payment Date *",
            helper_text="YYYY-MM-DD",
            helper_text_mode="on_error",
            text=get_current_date(),
            size_hint_y=None, height=dp(56),
        )
        self._pmt_method_btn = MDRaisedButton(
            text=f"Method: {self._payment_method}  ▼",
            md_bg_color=[0.10, 0.14, 0.49, 0.1],
            theme_text_color="Custom",
            text_color=[0.10, 0.14, 0.49, 1],
            size_hint_x=1, height=dp(44),
            on_release=self._open_method_menu,
        )
        self._pmt_notes = MDTextField(
            hint_text="Notes (optional)",
            size_hint_y=None, height=dp(48),
        )

        btn_row = MDBoxLayout(
            orientation="horizontal", spacing=dp(8),
            size_hint_y=None, height=dp(48),
        )
        cancel_btn = MDFlatButton(
            text="CANCEL",
            theme_text_color="Custom",
            text_color=[0.96, 0.26, 0.21, 1],
            size_hint_x=0.35,
            on_release=lambda _b: self._load_data(),
        )
        submit_btn = MDRaisedButton(
            text="SUBMIT PAYMENT",
            md_bg_color=[0.23, 0.62, 0.27, 1],
            size_hint_x=0.65, height=dp(44),
            on_release=lambda _b, r=remaining: self._submit_payment(r),
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(submit_btn)

        for w in [self._pmt_amount, self._pmt_date,
                  self._pmt_method_btn, self._pmt_notes, btn_row]:
            form_col.add_widget(w)
        form_card.add_widget(form_col)
        self._content.add_widget(form_card)
        # Scroll to bottom
        Clock.schedule_once(lambda _dt: setattr(self._scroll, "scroll_y", 0), 0.1)

    def _open_method_menu(self, btn) -> None:
        items = [
            {
                "text": m,
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda x=m: self._select_method(x),
            }
            for m in PAYMENT_METHODS
        ]
        self._method_menu = MDDropdownMenu(
            caller=btn, items=items, width_mult=4, max_height=dp(220),
        )
        self._method_menu.open()

    def _select_method(self, method: str) -> None:
        self._payment_method = method
        self._pmt_method_btn.text = f"Method: {method}  ▼"
        if self._method_menu:
            self._method_menu.dismiss()

    def _submit_payment(self, max_allowed: float) -> None:
        """Validate and record the payment."""
        valid_amt, msg_amt = validate_payment_amount(self._pmt_amount.text, max_allowed)
        if not valid_amt:
            self._pmt_amount.error = True
            self._pmt_amount.helper_text = msg_amt
            show_error_dialog("Invalid Amount", msg_amt)
            return
        valid_date, msg_date = validate_date(self._pmt_date.text)
        if not valid_date:
            self._pmt_date.error = True
            self._pmt_date.helper_text = msg_date
            show_error_dialog("Invalid Date", msg_date)
            return

        app = App.get_running_app()
        if app is None:
            return
        payment_id = app.db.record_payment(
            fee_id=self._selected_fee["id"],
            student_id=self._student_id,
            amount_paid=float(self._pmt_amount.text.strip()),
            payment_date=self._pmt_date.text.strip(),
            payment_method=self._payment_method,
            notes=self._pmt_notes.text.strip(),
        )
        if payment_id:
            show_success_dialog("Payment Recorded", "Payment has been saved successfully.")
            Clock.schedule_once(lambda _dt: self._load_data(), 0.3)
        else:
            show_error_dialog("Payment Failed", "Could not record payment. Please try again.")

    # ------------------------------------------------------------------
    # Voucher generation
    # ------------------------------------------------------------------

    def _generate_voucher(self, fee: dict) -> None:
        from libs.pdf_generator import VoucherGenerator

        app = App.get_running_app()
        if app is None:
            return
        voucher_number = app.db.generate_voucher_number()
        filename = generate_filename(f"Voucher_{self._student_id}_{fee.get('month', '')}", "pdf")
        output_path = os.path.join(get_vouchers_path(), filename)

        gen = VoucherGenerator()
        path = gen.generate_fee_voucher(
            student_data=self._student,
            fee_data=fee,
            voucher_number=voucher_number,
            output_path=output_path,
        )
        if path:
            app.db.save_voucher_record(fee["id"], self._student_id, voucher_number, path)
            show_success_dialog("Voucher Generated", f"Saved to:\n{path}")
        else:
            show_error_dialog("Voucher Failed", "Could not generate PDF voucher.")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _go_back(self) -> None:
        app = App.get_running_app()
        if app:
            app.go_back()
