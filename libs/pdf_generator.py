"""
PDF generation for Khan'z Academy Mobile App.

Contains two classes:
    VoucherGenerator  — generates individual fee voucher PDFs
    ReportGenerator   — generates management report PDFs

All output uses the FPDF2 library (fpdf2 package).
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fpdf import FPDF  # type: ignore

from libs.utils import (
    format_currency,
    format_date,
    format_month_year,
    get_reports_path,
    get_vouchers_path,
    log_error,
)


# ---------------------------------------------------------------------------
# Colour constants (RGB tuples)
# ---------------------------------------------------------------------------

COLOR_PRIMARY = (26, 35, 126)        # Deep Blue  #1a237e
COLOR_PRIMARY_LIGHT = (83, 75, 174)  # #534bae
COLOR_ACCENT = (255, 193, 7)         # Amber      #ffc107
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GRAY = (245, 245, 245)   # #f5f5f5
COLOR_MID_GRAY = (117, 117, 117)     # #757575
COLOR_DARK = (33, 33, 33)            # #212121
COLOR_SUCCESS = (76, 175, 80)        # Green      #4caf50
COLOR_ERROR = (244, 67, 54)          # Red        #f44336
COLOR_WARNING = (255, 152, 0)        # Orange     #ff9800
COLOR_ROW_ALT = (245, 245, 245)      # alternating row background


# ---------------------------------------------------------------------------
# Base PDF class with shared header/footer helpers
# ---------------------------------------------------------------------------

class _BasePDF(FPDF):
    """Internal base FPDF subclass providing Khan'z Academy branding helpers."""

    @staticmethod
    def _ascii_safe(text: str) -> str:
        """Replace non-Latin-1 characters with close ASCII equivalents."""
        replacements = {
            "\u2014": "-",  # em dash
            "\u2013": "-",  # en dash
            "\u2019": "'",  # right single quotation
            "\u2018": "'",  # left single quotation
            "\u201c": '"',  # left double quotation
            "\u201d": '"',  # right double quotation
            "\u2026": "...", # ellipsis
            "\u20a8": "Rs.", # rupee sign
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        # Final fallback: encode to latin-1, replacing anything unrepresentable
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def add_academy_header(self, subtitle: str = "") -> None:
        """Render the standard academy header at the current Y position."""
        # Academy name
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*COLOR_PRIMARY)
        self.cell(0, 10, "KHAN'Z ACADEMY", align="C", ln=True)

        # Tagline
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(*COLOR_MID_GRAY)
        self.cell(0, 6, "Excellence in Education", align="C", ln=True)

        if subtitle:
            self.ln(2)
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(*COLOR_PRIMARY)
            safe_subtitle = self._ascii_safe(subtitle)
            self.cell(0, 8, safe_subtitle, align="C", ln=True)

        # Divider line
        self.ln(2)
        self._draw_divider()
        self.ln(4)

    def _draw_divider(self) -> None:
        """Draw a full-width horizontal rule in the primary colour."""
        self.set_draw_color(*COLOR_PRIMARY)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(),
                  self.w - self.r_margin, self.get_y())
        self.set_line_width(0.2)
        self.set_draw_color(0, 0, 0)

    def add_academy_footer(self) -> None:
        """Render the standard footer block at the current Y position."""
        self.ln(4)
        self._draw_divider()
        self.ln(3)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*COLOR_MID_GRAY)
        self.cell(0, 5, "This is a computer-generated document.", align="C", ln=True)
        self.cell(0, 5, "For queries, contact KHAN'Z ACADEMY management.", align="C", ln=True)
        gen_ts = datetime.now().strftime("%d %B %Y  %H:%M")
        self.cell(0, 5, f"Generated: {gen_ts}  |  Thank you for choosing KHAN'Z ACADEMY!",
                  align="C", ln=True)

    def _label_value_row(
        self,
        label: str,
        value: str,
        fill: bool = False,
        label_width: float = 55,
    ) -> None:
        """Render a two-column label–value row with optional fill background."""
        row_height = 8
        available = self.w - self.l_margin - self.r_margin
        value_width = available - label_width

        if fill:
            self.set_fill_color(*COLOR_ROW_ALT)
        else:
            self.set_fill_color(*COLOR_WHITE)

        # Label cell
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*COLOR_DARK)
        self.cell(label_width, row_height, label, border=0, fill=True)

        # Value cell
        self.set_font("Helvetica", "", 10)
        self.cell(value_width, row_height, str(value), border=0, fill=True, ln=True)

    def _status_color(self, status: str) -> tuple:
        """Return the RGB tuple for a fee status label."""
        mapping = {
            "Paid": COLOR_SUCCESS,
            "Unpaid": COLOR_ERROR,
            "Partial": COLOR_WARNING,
        }
        return mapping.get(status, COLOR_DARK)


# ---------------------------------------------------------------------------
# VoucherGenerator
# ---------------------------------------------------------------------------

class VoucherGenerator:
    """Generate individual fee voucher PDFs for Khan'z Academy."""

    def generate_fee_voucher(
        self,
        student_data: Dict[str, Any],
        fee_data: Dict[str, Any],
        voucher_number: str,
        output_path: str,
    ) -> Optional[str]:
        """
        Generate a PDF fee voucher and save it to *output_path*.

        Parameters
        ----------
        student_data : dict
            Keys: student_name, father_name, class_name, phone_number,
                  admission_date
        fee_data : dict
            Keys: month, fee_amount, paid_amount, due_date, status
        voucher_number : str
            Unique voucher identifier (e.g. KA-20260413-0001)
        output_path : str
            Full file-system path where the PDF will be saved.

        Returns
        -------
        str
            The saved file path on success, or None on failure.
        """
        try:
            pdf = _BasePDF(orientation="P", unit="mm", format="A5")
            pdf.set_margins(left=15, top=15, right=15)
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # ---- Header ----
            pdf.add_academy_header("FEE VOUCHER")

            # Voucher meta (right-aligned)
            issue_date = datetime.now().strftime("%d %B %Y")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*COLOR_MID_GRAY)
            pdf.cell(0, 5, f"Voucher No: {voucher_number}", align="R", ln=True)
            pdf.cell(0, 5, f"Issue Date: {issue_date}", align="R", ln=True)
            pdf.ln(4)

            # ---- Student Details ----
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*COLOR_PRIMARY)
            pdf.cell(0, 7, "STUDENT DETAILS", ln=True)
            pdf.ln(1)

            student_rows = [
                ("Student Name", student_data.get("student_name", "")),
                ("Father Name",  student_data.get("father_name", "")),
                ("Class",        student_data.get("class_name", "")),
                ("Phone",        student_data.get("phone_number", "")),
                ("Admission Date",
                 format_date(student_data.get("admission_date", ""))),
            ]
            for idx, (label, value) in enumerate(student_rows):
                pdf._label_value_row(label, value, fill=(idx % 2 == 0))
            pdf.ln(5)

            # ---- Fee Details ----
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*COLOR_PRIMARY)
            pdf.cell(0, 7, "FEE DETAILS", ln=True)
            pdf.ln(1)

            fee_amount = float(fee_data.get("fee_amount", 0))
            paid_amount = float(fee_data.get("paid_amount", 0))
            balance_due = max(0.0, fee_amount - paid_amount)
            status = fee_data.get("status", "Unpaid")
            month_label = format_month_year(fee_data.get("month", ""))

            fee_rows = [
                ("Fee Month",    month_label),
                ("Fee Amount",   format_currency(fee_amount)),
                ("Amount Paid",  format_currency(paid_amount)),
                ("Balance Due",  format_currency(balance_due)),
                ("Due Date",     format_date(fee_data.get("due_date", ""))),
            ]
            for idx, (label, value) in enumerate(fee_rows):
                pdf._label_value_row(label, value, fill=(idx % 2 == 0))

            # Status row — coloured text
            status_row_h = 8
            available = pdf.w - pdf.l_margin - pdf.r_margin
            label_w = 55
            pdf.set_fill_color(*COLOR_ROW_ALT)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*COLOR_DARK)
            pdf.cell(label_w, status_row_h, "Status", border=0, fill=True)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*pdf._status_color(status))
            pdf.cell(available - label_w, status_row_h, status,
                     border=0, fill=True, ln=True)

            # ---- Footer ----
            pdf.add_academy_footer()

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pdf.output(output_path)
            return output_path

        except Exception as exc:
            log_error("VoucherGenerator.generate_fee_voucher failed", exc)
            return None


# ---------------------------------------------------------------------------
# ReportGenerator
# ---------------------------------------------------------------------------

class ReportGenerator:
    """Generate management report PDFs for Khan'z Academy."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _new_report_pdf() -> _BasePDF:
        """Return a fresh A4 portrait PDF instance."""
        pdf = _BasePDF(orientation="P", unit="mm", format="A4")
        pdf.set_margins(left=15, top=15, right=15)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        return pdf

    @staticmethod
    def _table_header(
        pdf: _BasePDF,
        headers: List[str],
        col_widths: List[float],
        row_height: float = 9,
    ) -> None:
        """Render a styled table header row."""
        pdf.set_fill_color(*COLOR_PRIMARY)
        pdf.set_text_color(*COLOR_WHITE)
        pdf.set_font("Helvetica", "B", 9)
        for header, width in zip(headers, col_widths):
            pdf.cell(width, row_height, header, border=0, fill=True, align="C")
        pdf.ln(row_height)

    @staticmethod
    def _table_row(
        pdf: _BasePDF,
        cells: List[str],
        col_widths: List[float],
        fill: bool = False,
        row_height: float = 8,
        alignments: Optional[List[str]] = None,
    ) -> None:
        """Render a single data row in the table."""
        if fill:
            pdf.set_fill_color(*COLOR_ROW_ALT)
        else:
            pdf.set_fill_color(*COLOR_WHITE)
        pdf.set_text_color(*COLOR_DARK)
        pdf.set_font("Helvetica", "", 8)

        if alignments is None:
            alignments = ["L"] * len(cells)

        for cell_text, width, align in zip(cells, col_widths, alignments):
            pdf.cell(width, row_height, str(cell_text), border=0,
                     fill=True, align=align)
        pdf.ln(row_height)

    @staticmethod
    def _save_pdf(pdf: _BasePDF, dest_dir: str, filename: str) -> Optional[str]:
        """Save the PDF to *dest_dir/filename* and return the path."""
        try:
            os.makedirs(dest_dir, exist_ok=True)
            path = os.path.join(dest_dir, filename)
            pdf.output(path)
            return path
        except Exception as exc:
            log_error("ReportGenerator._save_pdf failed", exc)
            return None

    # ------------------------------------------------------------------
    # Monthly Income Report
    # ------------------------------------------------------------------

    def generate_monthly_income_report(
        self,
        month_str: str,
        fee_records: List[Dict[str, Any]],
        summary: Dict[str, float],
    ) -> Optional[str]:
        """
        Generate a monthly income report PDF.

        Parameters
        ----------
        month_str : str   YYYY-MM
        fee_records : list of fee dicts (with student_name, class_name, etc.)
        summary : dict    Keys: total_expected, total_collected, total_pending
        """
        try:
            pdf = self._new_report_pdf()
            month_label = format_month_year(month_str)
            pdf.add_academy_header(f"Monthly Income Report - {month_label}")

            # Summary cards row
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*COLOR_PRIMARY)
            pdf.cell(0, 7, "SUMMARY", ln=True)
            pdf.ln(1)

            summary_items = [
                ("Total Expected",   format_currency(summary.get("total_expected", 0))),
                ("Total Collected",  format_currency(summary.get("total_collected", 0))),
                ("Total Pending",    format_currency(summary.get("total_pending", 0))),
            ]
            expected = summary.get("total_expected", 0)
            collected = summary.get("total_collected", 0)
            rate = (collected / expected * 100) if expected > 0 else 0.0
            summary_items.append(("Collection Rate", f"{rate:.1f}%"))

            for idx, (label, value) in enumerate(summary_items):
                pdf._label_value_row(label, value, fill=(idx % 2 == 0))
            pdf.ln(6)

            # Detailed table
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*COLOR_PRIMARY)
            pdf.cell(0, 7, "DETAILED RECORDS", ln=True)
            pdf.ln(1)

            headers = ["#", "Student Name", "Class", "Fee Amount", "Paid", "Status"]
            available = pdf.w - pdf.l_margin - pdf.r_margin
            col_widths = [10, available * 0.32, available * 0.14,
                          available * 0.16, available * 0.16, available * 0.16]
            self._table_header(pdf, headers, col_widths)

            for idx, record in enumerate(fee_records):
                status = record.get("status", "Unpaid")
                cells = [
                    str(idx + 1),
                    record.get("student_name", ""),
                    record.get("class_name", ""),
                    format_currency(record.get("fee_amount", 0)),
                    format_currency(record.get("paid_amount", 0)),
                    status,
                ]
                self._table_row(pdf, cells, col_widths,
                                fill=(idx % 2 == 0),
                                alignments=["C", "L", "C", "R", "R", "C"])
                # Colour the status cell separately
                # (FPDF renders cells left-to-right; we handle colour via text only)

            pdf.add_academy_footer()

            month_label_safe = month_label.replace(" ", "_")
            filename = f"Income_Report_{month_label_safe}.pdf"
            return self._save_pdf(pdf, get_reports_path(), filename)

        except Exception as exc:
            log_error("ReportGenerator.generate_monthly_income_report failed", exc)
            return None

    # ------------------------------------------------------------------
    # Defaulters Report
    # ------------------------------------------------------------------

    def generate_defaulters_report(
        self,
        month_str: str,
        defaulters: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Generate a defaulters (unpaid/partial fees) report PDF."""
        try:
            pdf = self._new_report_pdf()
            month_label = format_month_year(month_str)
            pdf.add_academy_header(f"Defaulters Report - {month_label}")

            # Total outstanding
            total_outstanding = sum(
                float(d.get("fee_amount", 0)) - float(d.get("paid_amount", 0))
                for d in defaulters
            )
            pdf._label_value_row("Total Defaulters", str(len(defaulters)), fill=True)
            pdf._label_value_row("Total Outstanding",
                                 format_currency(total_outstanding), fill=False)
            pdf.ln(6)

            headers = ["#", "Student Name", "Father Name", "Class",
                       "Phone", "Fee Amt", "Paid", "Balance"]
            available = pdf.w - pdf.l_margin - pdf.r_margin
            col_w = [8, available * 0.20, available * 0.17, available * 0.09,
                     available * 0.14, available * 0.11,
                     available * 0.10, available * 0.11]
            self._table_header(pdf, headers, col_w)

            for idx, record in enumerate(defaulters):
                fee_amt = float(record.get("fee_amount", 0))
                paid = float(record.get("paid_amount", 0))
                balance = max(0.0, fee_amt - paid)
                cells = [
                    str(idx + 1),
                    record.get("student_name", ""),
                    record.get("father_name", ""),
                    record.get("class_name", ""),
                    record.get("phone_number", ""),
                    format_currency(fee_amt),
                    format_currency(paid),
                    format_currency(balance),
                ]
                self._table_row(pdf, cells, col_w, fill=(idx % 2 == 0),
                                alignments=["C", "L", "L", "C", "C", "R", "R", "R"])

            pdf.add_academy_footer()
            filename = f"Defaulters_Report_{month_label.replace(' ', '_')}.pdf"
            return self._save_pdf(pdf, get_reports_path(), filename)

        except Exception as exc:
            log_error("ReportGenerator.generate_defaulters_report failed", exc)
            return None

    # ------------------------------------------------------------------
    # Class-wise Report
    # ------------------------------------------------------------------

    def generate_class_wise_report(
        self,
        class_data: List[Dict[str, Any]],
        students_by_class: Dict[int, List[Dict[str, Any]]],
    ) -> Optional[str]:
        """
        Generate a class-wise summary + student listing report PDF.

        Parameters
        ----------
        class_data : list of class dicts (class_name, class_number,
                      student_count, total_fees)
        students_by_class : dict mapping class_id → list of student dicts
        """
        try:
            pdf = self._new_report_pdf()
            pdf.add_academy_header("Class-wise Report")

            # Summary table
            headers = ["Class", "Students", "Monthly Fee Potential"]
            available = pdf.w - pdf.l_margin - pdf.r_margin
            col_w = [available * 0.40, available * 0.25, available * 0.35]
            self._table_header(pdf, headers, col_w)

            for idx, cls in enumerate(class_data):
                cells = [
                    cls.get("class_name", ""),
                    str(cls.get("student_count", 0)),
                    format_currency(cls.get("total_fees", 0)),
                ]
                self._table_row(pdf, cells, col_w, fill=(idx % 2 == 0),
                                alignments=["L", "C", "R"])
            pdf.ln(8)

            # Per-class student listing
            for cls in class_data:
                class_id = cls.get("id", 0)
                students = students_by_class.get(class_id, [])
                if not students:
                    continue

                # Class heading
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(*COLOR_PRIMARY)
                pdf.cell(0, 7, cls.get("class_name", ""), ln=True)
                pdf.ln(1)

                s_headers = ["#", "Student Name", "Father Name", "Phone", "Monthly Fee"]
                s_col_w = [8, available * 0.32, available * 0.27,
                           available * 0.20, available * 0.17]
                self._table_header(pdf, s_headers, s_col_w)

                for sidx, student in enumerate(students):
                    cells = [
                        str(sidx + 1),
                        student.get("student_name", ""),
                        student.get("father_name", ""),
                        student.get("phone_number", ""),
                        format_currency(student.get("monthly_fee", 0)),
                    ]
                    self._table_row(pdf, cells, s_col_w,
                                    fill=(sidx % 2 == 0),
                                    alignments=["C", "L", "L", "C", "R"])
                pdf.ln(5)

            pdf.add_academy_footer()
            from libs.utils import generate_filename
            filename = generate_filename("Class_Wise_Report")
            return self._save_pdf(pdf, get_reports_path(), filename)

        except Exception as exc:
            log_error("ReportGenerator.generate_class_wise_report failed", exc)
            return None

    # ------------------------------------------------------------------
    # Student Directory
    # ------------------------------------------------------------------

    def generate_student_directory(
        self,
        students: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Generate a complete active student directory report PDF."""
        try:
            pdf = self._new_report_pdf()
            pdf.add_academy_header("Student Directory")

            pdf._label_value_row("Total Active Students", str(len(students)), fill=True)
            pdf.ln(6)

            headers = ["#", "Name", "Father Name", "Class",
                       "Phone", "Address", "Monthly Fee"]
            available = pdf.w - pdf.l_margin - pdf.r_margin
            col_w = [8, available * 0.20, available * 0.18, available * 0.09,
                     available * 0.13, available * 0.22, available * 0.14]
            self._table_header(pdf, headers, col_w)

            for idx, student in enumerate(students):
                address = student.get("address", "")
                if len(address) > 25:
                    address = address[:22] + "..."
                cells = [
                    str(idx + 1),
                    student.get("student_name", ""),
                    student.get("father_name", ""),
                    student.get("class_name", ""),
                    student.get("phone_number", ""),
                    address,
                    format_currency(student.get("monthly_fee", 0)),
                ]
                self._table_row(pdf, cells, col_w, fill=(idx % 2 == 0),
                                alignments=["C", "L", "L", "C", "C", "L", "R"])

            pdf.add_academy_footer()
            from libs.utils import generate_filename
            filename = generate_filename("Student_Directory")
            return self._save_pdf(pdf, get_reports_path(), filename)

        except Exception as exc:
            log_error("ReportGenerator.generate_student_directory failed", exc)
            return None
