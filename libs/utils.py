"""
Utility functions for Khan'z Academy Mobile App.

Provides path resolution, date/currency formatting, and platform detection
helpers used throughout the application.
"""

import os
import sys
from datetime import date, datetime
from typing import Tuple


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def get_platform() -> str:
    """Return 'android' when running on Android, 'desktop' otherwise."""
    try:
        from kivy.utils import platform as kivy_platform  # type: ignore
        if kivy_platform == "android":
            return "android"
    except Exception:
        pass
    return "desktop"


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def get_base_path() -> str:
    """
    Return the application's base directory.

    On Android this is the app's private external storage directory.
    On desktop it is the directory containing this file (project root).
    """
    if get_platform() == "android":
        try:
            from android.storage import app_storage_path  # type: ignore  # noqa: F401
            # Use Kivy's user_data_dir which maps to Android private storage
            from kivy.app import App  # type: ignore
            app = App.get_running_app()
            if app is not None:
                return app.user_data_dir
        except Exception:
            pass
        # Fallback: /sdcard/KhanzAcademy
        return "/sdcard/KhanzAcademy"
    # Desktop: two levels up from this file → project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_path() -> str:
    """Return the absolute path to the data/ directory."""
    return os.path.join(get_base_path(), "data")


def get_vouchers_path() -> str:
    """Return the absolute path to the vouchers/ directory."""
    return os.path.join(get_base_path(), "vouchers")


def get_reports_path() -> str:
    """Return the absolute path to the reports/ directory."""
    return os.path.join(get_base_path(), "reports")


def get_backups_path() -> str:
    """Return the absolute path to the backups/ directory."""
    return os.path.join(get_base_path(), "backups")


def get_db_path() -> str:
    """Return the absolute path to the SQLite database file."""
    return os.path.join(get_data_path(), "khanz_academy.db")


def get_log_path() -> str:
    """Return the absolute path to the error log file."""
    return os.path.join(get_data_path(), "error.log")


def ensure_folders_exist() -> None:
    """Create all required application directories if they do not exist."""
    for folder in (
        get_data_path(),
        get_vouchers_path(),
        get_reports_path(),
        get_backups_path(),
    ):
        os.makedirs(folder, exist_ok=True)


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def get_current_date() -> str:
    """Return today's date as a YYYY-MM-DD string."""
    return date.today().strftime("%Y-%m-%d")


def get_current_month_year() -> Tuple[int, int]:
    """Return a (month_number, year) tuple for today's date."""
    today = date.today()
    return today.month, today.year


def get_month_name(month_number: int) -> str:
    """Return the full English month name for a given month number (1-12)."""
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    }
    return month_names.get(month_number, "Unknown")


def format_date(
    date_str: str,
    input_format: str = "%Y-%m-%d",
    output_format: str = "%d %B %Y",
) -> str:
    """
    Convert a date string from *input_format* to *output_format*.

    Returns the original string unchanged if parsing fails.
    """
    try:
        parsed = datetime.strptime(date_str, input_format)
        return parsed.strftime(output_format)
    except (ValueError, TypeError):
        return date_str


def format_month_year(month_str: str) -> str:
    """
    Convert a YYYY-MM string to a human-readable 'Month YYYY' label.

    Example: '2026-04' → 'April 2026'
    """
    try:
        parsed = datetime.strptime(month_str, "%Y-%m")
        return parsed.strftime("%B %Y")
    except (ValueError, TypeError):
        return month_str


# ---------------------------------------------------------------------------
# Currency / number helpers
# ---------------------------------------------------------------------------

def format_currency(amount: float) -> str:
    """
    Format a numeric amount as a Pakistani Rupee string.

    Example: 1500.0 → 'Rs. 1,500.00'
    """
    try:
        return f"Rs. {float(amount):,.2f}"
    except (ValueError, TypeError):
        return "Rs. 0.00"


# ---------------------------------------------------------------------------
# File-name helpers
# ---------------------------------------------------------------------------

def generate_filename(prefix: str, extension: str = "pdf") -> str:
    """
    Return a timestamped filename string.

    Example: generate_filename('Income_Report') → 'Income_Report_20260413_143022.pdf'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = extension.lstrip(".")
    return f"{prefix}_{timestamp}.{ext}"


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------

def log_error(message: str, exc: Exception = None) -> None:  # type: ignore[assignment]
    """
    Append an error entry to the application error log.

    Silently ignores any I/O errors to avoid secondary crashes.
    """
    import traceback

    try:
        ensure_folders_exist()
        log_path = get_log_path()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n[{timestamp}] {message}\n")
            if exc is not None:
                log_file.write(traceback.format_exc())
                log_file.write("\n")
    except Exception:
        pass
