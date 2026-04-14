"""
SQLite database manager for Khan'z Academy Mobile App.

Provides a single DatabaseManager class that encapsulates all CRUD
operations, using parameterised queries throughout to prevent SQL
injection.  Every public method handles its own exceptions and never
raises to the caller.
"""

import sqlite3
import shutil
import os
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Any

from libs.utils import get_db_path, get_backups_path, generate_filename, log_error


# ---------------------------------------------------------------------------
# Schema SQL
# ---------------------------------------------------------------------------

_CREATE_CLASSES_TABLE = """
CREATE TABLE IF NOT EXISTS classes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name   TEXT    NOT NULL UNIQUE,
    class_number INTEGER NOT NULL UNIQUE
);
"""

_CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name   TEXT    NOT NULL,
    father_name    TEXT    NOT NULL,
    class_id       INTEGER NOT NULL REFERENCES classes(id),
    phone_number   TEXT    NOT NULL,
    address        TEXT    DEFAULT '',
    admission_date TEXT    NOT NULL,
    monthly_fee    REAL    NOT NULL CHECK(monthly_fee > 0),
    is_active      INTEGER DEFAULT 1,
    created_at     TEXT    DEFAULT CURRENT_TIMESTAMP,
    updated_at     TEXT    DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_FEES_TABLE = """
CREATE TABLE IF NOT EXISTS fees (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    month       TEXT    NOT NULL,
    fee_amount  REAL    NOT NULL,
    paid_amount REAL    DEFAULT 0,
    status      TEXT    DEFAULT 'Unpaid'
                        CHECK(status IN ('Paid', 'Unpaid', 'Partial')),
    due_date    TEXT    NOT NULL,
    created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_PAYMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS payments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    fee_id         INTEGER NOT NULL REFERENCES fees(id),
    student_id     INTEGER NOT NULL REFERENCES students(id),
    amount_paid    REAL    NOT NULL CHECK(amount_paid > 0),
    payment_date   TEXT    NOT NULL,
    payment_method TEXT    DEFAULT 'Cash',
    notes          TEXT    DEFAULT '',
    created_at     TEXT    DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_VOUCHERS_TABLE = """
CREATE TABLE IF NOT EXISTS vouchers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    fee_id         INTEGER NOT NULL REFERENCES fees(id),
    student_id     INTEGER NOT NULL REFERENCES students(id),
    voucher_number TEXT    NOT NULL UNIQUE,
    file_path      TEXT    NOT NULL,
    generated_at   TEXT    DEFAULT CURRENT_TIMESTAMP
);
"""

_SEED_CLASSES = [
    ("Class 1", 1), ("Class 2", 2), ("Class 3", 3),
    ("Class 4", 4), ("Class 5", 5), ("Class 6", 6),
    ("Class 7", 7), ("Class 8", 8), ("Class 9", 9),
    ("Class 10", 10), ("Class 11", 11), ("Class 12", 12),
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _row_to_dict(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    """Convert a sqlite3 row tuple to a dictionary keyed by column name."""
    return {description[0]: value for description, value in zip(cursor.description, row)}


def _rows_to_dicts(cursor: sqlite3.Cursor, rows: List[tuple]) -> List[Dict[str, Any]]:
    """Convert a list of sqlite3 row tuples to a list of dicts."""
    if not rows:
        return []
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


# ---------------------------------------------------------------------------
# DatabaseManager
# ---------------------------------------------------------------------------

class DatabaseManager:
    """
    Central database access object for Khan'z Academy.

    Usage::

        db = DatabaseManager()
        db.initialise()
        students = db.get_all_students()
    """

    def __init__(self) -> None:
        self._db_path: str = get_db_path()

    # ------------------------------------------------------------------
    # Internal connection helper
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        """Open and return a new database connection with row_factory set."""
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def initialise(self) -> None:
        """Create all tables and seed class data on first run."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                for ddl in (
                    _CREATE_CLASSES_TABLE,
                    _CREATE_STUDENTS_TABLE,
                    _CREATE_FEES_TABLE,
                    _CREATE_PAYMENTS_TABLE,
                    _CREATE_VOUCHERS_TABLE,
                ):
                    cursor.execute(ddl)
                # Seed classes only if table is empty
                cursor.execute("SELECT COUNT(*) FROM classes;")
                count = cursor.fetchone()[0]
                if count == 0:
                    cursor.executemany(
                        "INSERT INTO classes (class_name, class_number) VALUES (?, ?);",
                        _SEED_CLASSES,
                    )
                conn.commit()
        except Exception as exc:
            log_error("DatabaseManager.initialise failed", exc)

    # ==================================================================
    # STUDENT METHODS
    # ==================================================================

    def add_student(
        self,
        student_name: str,
        father_name: str,
        class_id: int,
        phone_number: str,
        address: str,
        admission_date: str,
        monthly_fee: float,
    ) -> Optional[int]:
        """
        Insert a new student record.

        Returns the new student's integer ID, or None on failure.
        """
        sql = """
            INSERT INTO students
                (student_name, father_name, class_id, phone_number,
                 address, admission_date, monthly_fee)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    sql,
                    (student_name.strip(), father_name.strip(), int(class_id),
                     phone_number.strip(), address.strip(), admission_date,
                     float(monthly_fee)),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as exc:
            log_error("DatabaseManager.add_student failed", exc)
            return None

    def update_student(self, student_id: int, **kwargs) -> bool:
        """
        Update one or more fields on an existing student record.

        Only the keyword-argument keys that match valid column names are
        written; unknown keys are ignored.  Returns True on success.
        """
        allowed_columns = {
            "student_name", "father_name", "class_id", "phone_number",
            "address", "admission_date", "monthly_fee", "is_active",
        }
        fields = {k: v for k, v in kwargs.items() if k in allowed_columns}
        if not fields:
            return False
        fields["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        set_clause = ", ".join(f"{col} = ?" for col in fields)
        values = list(fields.values()) + [student_id]
        sql = f"UPDATE students SET {set_clause} WHERE id = ?;"
        try:
            with self._connect() as conn:
                conn.execute(sql, values)
                conn.commit()
            return True
        except Exception as exc:
            log_error("DatabaseManager.update_student failed", exc)
            return False

    def delete_student(self, student_id: int) -> bool:
        """
        Soft-delete a student by setting is_active = 0.

        Returns True on success.
        """
        return self.update_student(student_id, is_active=0)

    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Return a single student dict by ID, or None if not found."""
        sql = """
            SELECT s.*, c.class_name, c.class_number
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            WHERE s.id = ?;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (student_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return _row_to_dict(cursor, row)
        except Exception as exc:
            log_error("DatabaseManager.get_student failed", exc)
            return None

    def get_all_students(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Return all students, optionally filtered to active records only."""
        sql = """
            SELECT s.*, c.class_name, c.class_number
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            {where}
            ORDER BY c.class_number, s.student_name;
        """
        where = "WHERE s.is_active = 1" if active_only else ""
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql.format(where=where))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_all_students failed", exc)
            return []

    def search_students(self, query: str) -> List[Dict[str, Any]]:
        """Search active students by name (case-insensitive partial match)."""
        sql = """
            SELECT s.*, c.class_name, c.class_number
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            WHERE s.is_active = 1
              AND LOWER(s.student_name) LIKE LOWER(?)
            ORDER BY s.student_name;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (f"%{query}%",))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.search_students failed", exc)
            return []

    def filter_students_by_class(self, class_id: int) -> List[Dict[str, Any]]:
        """Return all active students belonging to a specific class."""
        sql = """
            SELECT s.*, c.class_name, c.class_number
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            WHERE s.is_active = 1 AND s.class_id = ?
            ORDER BY s.student_name;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (class_id,))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.filter_students_by_class failed", exc)
            return []

    def get_student_count(self) -> int:
        """Return the total number of active students."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) FROM students WHERE is_active = 1;"
                ).fetchone()
                return int(row[0]) if row else 0
        except Exception as exc:
            log_error("DatabaseManager.get_student_count failed", exc)
            return 0

    def get_student_count_by_class(self, class_id: int) -> int:
        """Return the number of active students in the given class."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) FROM students WHERE is_active = 1 AND class_id = ?;",
                    (class_id,),
                ).fetchone()
                return int(row[0]) if row else 0
        except Exception as exc:
            log_error("DatabaseManager.get_student_count_by_class failed", exc)
            return 0

    # ==================================================================
    # CLASS METHODS
    # ==================================================================

    def get_all_classes(self) -> List[Dict[str, Any]]:
        """Return all class records ordered by class_number."""
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    "SELECT * FROM classes ORDER BY class_number;"
                )
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_all_classes failed", exc)
            return []

    def get_class(self, class_id: int) -> Optional[Dict[str, Any]]:
        """Return a single class record by ID, or None."""
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    "SELECT * FROM classes WHERE id = ?;", (class_id,)
                )
                row = cursor.fetchone()
                return _row_to_dict(cursor, row) if row else None
        except Exception as exc:
            log_error("DatabaseManager.get_class failed", exc)
            return None

    def get_students_in_class(self, class_id: int) -> List[Dict[str, Any]]:
        """Return all active student records for the given class."""
        return self.filter_students_by_class(class_id)

    # ==================================================================
    # FEE METHODS
    # ==================================================================

    def generate_monthly_fees(self, month: int, year: int) -> Tuple[int, int]:
        """
        Create fee records for every active student for the given month/year.

        Skips students that already have a fee record for that month.
        Returns a (generated_count, skipped_count) tuple.
        """
        month_str = f"{year}-{month:02d}"
        due_date = f"{year}-{month:02d}-10"
        students = self.get_all_students(active_only=True)
        generated = 0
        skipped = 0
        sql_check = "SELECT id FROM fees WHERE student_id = ? AND month = ?;"
        sql_insert = """
            INSERT INTO fees (student_id, month, fee_amount, due_date)
            VALUES (?, ?, ?, ?);
        """
        try:
            with self._connect() as conn:
                for student in students:
                    row = conn.execute(
                        sql_check, (student["id"], month_str)
                    ).fetchone()
                    if row:
                        skipped += 1
                    else:
                        conn.execute(
                            sql_insert,
                            (student["id"], month_str,
                             float(student["monthly_fee"]), due_date),
                        )
                        generated += 1
                conn.commit()
        except Exception as exc:
            log_error("DatabaseManager.generate_monthly_fees failed", exc)
        return generated, skipped

    def get_fees_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        """Return all fee records for a student, newest month first."""
        sql = """
            SELECT f.*, s.student_name, s.father_name, c.class_name
            FROM fees f
            JOIN students s ON f.student_id = s.id
            JOIN classes c  ON s.class_id  = c.id
            WHERE f.student_id = ?
            ORDER BY f.month DESC;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (student_id,))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_fees_by_student failed", exc)
            return []

    def get_fees_by_month(self, month_str: str) -> List[Dict[str, Any]]:
        """Return all fee records for the given YYYY-MM month string."""
        sql = """
            SELECT f.*, s.student_name, s.father_name, s.phone_number,
                   c.class_name, c.class_number
            FROM fees f
            JOIN students s ON f.student_id = s.id
            JOIN classes c  ON s.class_id   = c.id
            WHERE f.month = ?
            ORDER BY c.class_number, s.student_name;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (month_str,))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_fees_by_month failed", exc)
            return []

    def get_unpaid_fees(self) -> List[Dict[str, Any]]:
        """Return all fee records that are not fully paid."""
        sql = """
            SELECT f.*, s.student_name, c.class_name
            FROM fees f
            JOIN students s ON f.student_id = s.id
            JOIN classes c  ON s.class_id   = c.id
            WHERE f.status != 'Paid'
            ORDER BY f.month DESC, s.student_name;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql)
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_unpaid_fees failed", exc)
            return []

    def get_defaulters(self, month_str: str) -> List[Dict[str, Any]]:
        """Return students with unpaid or partial fees for the given month."""
        sql = """
            SELECT f.*, s.student_name, s.father_name, s.phone_number,
                   c.class_name, c.class_number
            FROM fees f
            JOIN students s ON f.student_id = s.id
            JOIN classes c  ON s.class_id   = c.id
            WHERE f.month = ? AND f.status != 'Paid'
            ORDER BY c.class_number, s.student_name;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (month_str,))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_defaulters failed", exc)
            return []

    def update_fee_status(self, fee_id: int) -> bool:
        """Recalculate and persist a fee record's status field."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT fee_amount, paid_amount FROM fees WHERE id = ?;",
                    (fee_id,),
                ).fetchone()
                if row is None:
                    return False
                fee_amount, paid_amount = float(row[0]), float(row[1])
                if paid_amount <= 0:
                    status = "Unpaid"
                elif paid_amount >= fee_amount:
                    status = "Paid"
                else:
                    status = "Partial"
                conn.execute(
                    "UPDATE fees SET status = ? WHERE id = ?;",
                    (status, fee_id),
                )
                conn.commit()
            return True
        except Exception as exc:
            log_error("DatabaseManager.update_fee_status failed", exc)
            return False

    def get_fee(self, fee_id: int) -> Optional[Dict[str, Any]]:
        """Return a single fee record by its ID."""
        sql = """
            SELECT f.*, s.student_name, s.father_name, s.phone_number,
                   c.class_name
            FROM fees f
            JOIN students s ON f.student_id = s.id
            JOIN classes c  ON s.class_id   = c.id
            WHERE f.id = ?;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (fee_id,))
                row = cursor.fetchone()
                return _row_to_dict(cursor, row) if row else None
        except Exception as exc:
            log_error("DatabaseManager.get_fee failed", exc)
            return None

    # ==================================================================
    # PAYMENT METHODS
    # ==================================================================

    def record_payment(
        self,
        fee_id: int,
        student_id: int,
        amount_paid: float,
        payment_date: str,
        payment_method: str = "Cash",
        notes: str = "",
    ) -> Optional[int]:
        """
        Insert a payment record and update the associated fee's paid_amount.

        Returns the new payment's integer ID, or None on failure.
        """
        sql_insert = """
            INSERT INTO payments
                (fee_id, student_id, amount_paid, payment_date,
                 payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        sql_update_fee = """
            UPDATE fees
               SET paid_amount = paid_amount + ?
             WHERE id = ?;
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    sql_insert,
                    (fee_id, student_id, float(amount_paid), payment_date,
                     payment_method, notes),
                )
                payment_id = cursor.lastrowid
                conn.execute(sql_update_fee, (float(amount_paid), fee_id))
                conn.commit()
            # Recalculate status outside the first connection (avoids locking)
            self.update_fee_status(fee_id)
            return payment_id
        except Exception as exc:
            log_error("DatabaseManager.record_payment failed", exc)
            return None

    def get_payments_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        """Return all payment records for a student, newest first."""
        sql = """
            SELECT p.*, f.month, f.fee_amount
            FROM payments p
            JOIN fees f ON p.fee_id = f.id
            WHERE p.student_id = ?
            ORDER BY p.payment_date DESC;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (student_id,))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_payments_by_student failed", exc)
            return []

    def get_payments_by_fee(self, fee_id: int) -> List[Dict[str, Any]]:
        """Return all payment records for a specific fee record."""
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    "SELECT * FROM payments WHERE fee_id = ? ORDER BY payment_date DESC;",
                    (fee_id,),
                )
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_payments_by_fee failed", exc)
            return []

    # ==================================================================
    # VOUCHER METHODS
    # ==================================================================

    def generate_voucher_number(self) -> str:
        """
        Return a unique voucher number in the format KA-YYYYMMDD-XXXX.

        XXXX is a zero-padded sequential counter for the current date.
        """
        today_str = date.today().strftime("%Y%m%d")
        prefix = f"KA-{today_str}-"
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) FROM vouchers WHERE voucher_number LIKE ?;",
                    (f"{prefix}%",),
                ).fetchone()
                seq = (int(row[0]) if row else 0) + 1
        except Exception as exc:
            log_error("DatabaseManager.generate_voucher_number failed", exc)
            seq = 1
        return f"{prefix}{seq:04d}"

    def save_voucher_record(
        self,
        fee_id: int,
        student_id: int,
        voucher_number: str,
        file_path: str,
    ) -> Optional[int]:
        """Persist a voucher record and return its new ID."""
        sql = """
            INSERT INTO vouchers
                (fee_id, student_id, voucher_number, file_path)
            VALUES (?, ?, ?, ?);
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (fee_id, student_id, voucher_number, file_path))
                conn.commit()
                return cursor.lastrowid
        except Exception as exc:
            log_error("DatabaseManager.save_voucher_record failed", exc)
            return None

    def get_vouchers_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        """Return all voucher records for a student, newest first."""
        sql = """
            SELECT v.*, f.month, s.student_name, c.class_name
            FROM vouchers v
            JOIN fees     f ON v.fee_id     = f.id
            JOIN students s ON v.student_id = s.id
            JOIN classes  c ON s.class_id   = c.id
            WHERE v.student_id = ?
            ORDER BY v.generated_at DESC;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, (student_id,))
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_vouchers_by_student failed", exc)
            return []

    def get_all_vouchers(self) -> List[Dict[str, Any]]:
        """Return all voucher records with student details, newest first."""
        sql = """
            SELECT v.*, f.month, s.student_name, c.class_name
            FROM vouchers v
            JOIN fees     f ON v.fee_id     = f.id
            JOIN students s ON v.student_id = s.id
            JOIN classes  c ON s.class_id   = c.id
            ORDER BY v.generated_at DESC;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql)
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_all_vouchers failed", exc)
            return []

    # ==================================================================
    # REPORT METHODS
    # ==================================================================

    def get_monthly_income(self, month_str: str) -> float:
        """Return total amount paid for the given YYYY-MM month."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT COALESCE(SUM(paid_amount), 0) FROM fees WHERE month = ?;",
                    (month_str,),
                ).fetchone()
                return float(row[0]) if row else 0.0
        except Exception as exc:
            log_error("DatabaseManager.get_monthly_income failed", exc)
            return 0.0

    def get_monthly_income_detailed(self, month_str: str) -> List[Dict[str, Any]]:
        """Return per-student fee details for the given month."""
        return self.get_fees_by_month(month_str)

    def get_class_wise_report(self) -> List[Dict[str, Any]]:
        """Return a per-class summary of students, expected fees, collected, and pending."""
        sql = """
            SELECT c.class_name,
                   c.class_number,
                   COUNT(DISTINCT s.id)          AS student_count,
                   COALESCE(SUM(s.monthly_fee), 0) AS total_fees
            FROM classes c
            LEFT JOIN students s ON s.class_id = c.id AND s.is_active = 1
            GROUP BY c.id
            ORDER BY c.class_number;
        """
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql)
                return _rows_to_dicts(cursor, cursor.fetchall())
        except Exception as exc:
            log_error("DatabaseManager.get_class_wise_report failed", exc)
            return []

    def get_defaulters_report(self, month_str: str) -> List[Dict[str, Any]]:
        """Return defaulter records for the given month."""
        return self.get_defaulters(month_str)

    def get_fee_summary_for_month(self, month_str: str) -> Dict[str, float]:
        """
        Return a dict with total_expected, total_collected, and total_pending
        for the given YYYY-MM month.
        """
        sql = """
            SELECT COALESCE(SUM(fee_amount), 0)  AS total_expected,
                   COALESCE(SUM(paid_amount), 0) AS total_collected
            FROM fees
            WHERE month = ?;
        """
        try:
            with self._connect() as conn:
                row = conn.execute(sql, (month_str,)).fetchone()
                expected = float(row[0]) if row else 0.0
                collected = float(row[1]) if row else 0.0
                return {
                    "total_expected": expected,
                    "total_collected": collected,
                    "total_pending": max(0.0, expected - collected),
                }
        except Exception as exc:
            log_error("DatabaseManager.get_fee_summary_for_month failed", exc)
            return {"total_expected": 0.0, "total_collected": 0.0, "total_pending": 0.0}

    # ==================================================================
    # BACKUP METHOD
    # ==================================================================

    def backup_database(self) -> Optional[str]:
        """
        Copy the database file to the backups/ directory with a timestamp.

        Returns the backup file path on success, or None on failure.
        """
        try:
            backup_dir = get_backups_path()
            os.makedirs(backup_dir, exist_ok=True)
            filename = generate_filename("khanz_academy_backup", "db")
            dest = os.path.join(backup_dir, filename)
            shutil.copy2(self._db_path, dest)
            return dest
        except Exception as exc:
            log_error("DatabaseManager.backup_database failed", exc)
            return None
