"""
Input validation utilities for Khan'z Academy Mobile App.

Every public function returns a (is_valid: bool, error_message: str) tuple
and is guaranteed never to raise an unhandled exception.
"""

import re
from typing import Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_NAME_LENGTH: int = 2
MAX_NAME_LENGTH: int = 100
MIN_PHONE_LENGTH: int = 10
MAX_PHONE_LENGTH: int = 15
MAX_ADDRESS_LENGTH: int = 200
MAX_FEE_VALUE: float = 1_000_000.0
VALID_CLASS_IDS: range = range(1, 13)   # 1 through 12 inclusive

# Regex: letters (including accented) and spaces only
NAME_PATTERN: re.Pattern = re.compile(r"^[A-Za-z\s]+$")

# Regex: YYYY-MM-DD
DATE_PATTERN: re.Pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# Name validators
# ---------------------------------------------------------------------------

def validate_student_name(name: str) -> Tuple[bool, str]:
    """
    Validate a student's name.

    Rules:
    - Required (not empty after stripping whitespace)
    - Only alphabetic characters and spaces
    - Length between MIN_NAME_LENGTH and MAX_NAME_LENGTH characters
    """
    if not isinstance(name, str):
        return False, "Student name must be a text value."
    stripped = name.strip()
    if not stripped:
        return False, "Student name is required."
    if len(stripped) < MIN_NAME_LENGTH:
        return False, f"Student name must be at least {MIN_NAME_LENGTH} characters."
    if len(stripped) > MAX_NAME_LENGTH:
        return False, f"Student name must not exceed {MAX_NAME_LENGTH} characters."
    if not NAME_PATTERN.match(stripped):
        return False, "Student name may only contain letters and spaces."
    return True, ""


def validate_father_name(name: str) -> Tuple[bool, str]:
    """
    Validate a father's name.

    Applies the same rules as validate_student_name.
    """
    if not isinstance(name, str):
        return False, "Father name must be a text value."
    stripped = name.strip()
    if not stripped:
        return False, "Father name is required."
    if len(stripped) < MIN_NAME_LENGTH:
        return False, f"Father name must be at least {MIN_NAME_LENGTH} characters."
    if len(stripped) > MAX_NAME_LENGTH:
        return False, f"Father name must not exceed {MAX_NAME_LENGTH} characters."
    if not NAME_PATTERN.match(stripped):
        return False, "Father name may only contain letters and spaces."
    return True, ""


# ---------------------------------------------------------------------------
# Contact validators
# ---------------------------------------------------------------------------

def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate a phone number.

    Rules:
    - Required
    - Only digits (spaces and dashes are stripped before validation)
    - Length between MIN_PHONE_LENGTH and MAX_PHONE_LENGTH digits
    """
    if not isinstance(phone, str):
        return False, "Phone number must be a text value."
    cleaned = re.sub(r"[\s\-]", "", phone)
    if not cleaned:
        return False, "Phone number is required."
    if not cleaned.isdigit():
        return False, "Phone number must contain digits only (spaces and dashes are allowed)."
    if len(cleaned) < MIN_PHONE_LENGTH:
        return False, f"Phone number must be at least {MIN_PHONE_LENGTH} digits."
    if len(cleaned) > MAX_PHONE_LENGTH:
        return False, f"Phone number must not exceed {MAX_PHONE_LENGTH} digits."
    return True, ""


def validate_address(address: str) -> Tuple[bool, str]:
    """
    Validate an address (optional field).

    Rules:
    - May be empty
    - If provided, must not exceed MAX_ADDRESS_LENGTH characters
    """
    if not isinstance(address, str):
        return False, "Address must be a text value."
    if len(address) > MAX_ADDRESS_LENGTH:
        return False, f"Address must not exceed {MAX_ADDRESS_LENGTH} characters."
    return True, ""


# ---------------------------------------------------------------------------
# Fee / amount validators
# ---------------------------------------------------------------------------

def validate_monthly_fee(fee: str) -> Tuple[bool, str]:
    """
    Validate a monthly fee value entered as a string.

    Rules:
    - Required
    - Must parse as a positive float
    - Must be > 0
    - Must be ≤ MAX_FEE_VALUE
    """
    if not isinstance(fee, str):
        fee = str(fee)
    stripped = fee.strip()
    if not stripped:
        return False, "Monthly fee is required."
    try:
        value = float(stripped)
    except ValueError:
        return False, "Monthly fee must be a valid number."
    if value <= 0:
        return False, "Monthly fee must be greater than zero."
    if value > MAX_FEE_VALUE:
        return False, f"Monthly fee must not exceed Rs. {MAX_FEE_VALUE:,.0f}."
    return True, ""


def validate_payment_amount(amount: str, max_allowed: float) -> Tuple[bool, str]:
    """
    Validate a payment amount entered as a string.

    Rules:
    - Required
    - Must parse as a positive float
    - Must be > 0
    - Must be ≤ max_allowed
    """
    if not isinstance(amount, str):
        amount = str(amount)
    stripped = amount.strip()
    if not stripped:
        return False, "Payment amount is required."
    try:
        value = float(stripped)
    except ValueError:
        return False, "Payment amount must be a valid number."
    if value <= 0:
        return False, "Payment amount must be greater than zero."
    try:
        max_val = float(max_allowed)
    except (ValueError, TypeError):
        max_val = 0.0
    if value > max_val:
        return False, (
            f"Payment amount (Rs. {value:,.2f}) exceeds the remaining balance "
            f"(Rs. {max_val:,.2f})."
        )
    return True, ""


# ---------------------------------------------------------------------------
# Date validator
# ---------------------------------------------------------------------------

def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    Validate a date string in YYYY-MM-DD format.

    Rules:
    - Must match the pattern YYYY-MM-DD
    - Must represent a real calendar date
    """
    from datetime import datetime  # local import keeps module-level imports clean

    if not isinstance(date_str, str):
        return False, "Date must be a text value."
    stripped = date_str.strip()
    if not stripped:
        return False, "Date is required."
    if not DATE_PATTERN.match(stripped):
        return False, "Date must be in YYYY-MM-DD format (e.g., 2026-04-13)."
    try:
        datetime.strptime(stripped, "%Y-%m-%d")
    except ValueError:
        return False, "Please enter a valid calendar date."
    return True, ""


# ---------------------------------------------------------------------------
# Class selection validator
# ---------------------------------------------------------------------------

def validate_class_selection(class_id) -> Tuple[bool, str]:
    """
    Validate that a class has been selected and is within the valid range.

    Rules:
    - Must not be None or empty
    - Must be a valid integer class ID in VALID_CLASS_IDS (1-12)
    """
    if class_id is None or class_id == "" or class_id == "None":
        return False, "Please select a class."
    try:
        cid = int(class_id)
    except (ValueError, TypeError):
        return False, "Invalid class selection."
    if cid not in VALID_CLASS_IDS:
        return False, "Class must be between 1 and 12."
    return True, ""
