"""
Reusable custom Kivy/KivyMD widgets for Khan'z Academy Mobile App.
Premium Redesign - Soft Colors, Perfect Center Alignment, Proper MDIcons.

Defines:
    KACard         — a styled MDCard with consistent rounding & elevation
    KAStatCard     — a statistics card used on the dashboard
    KAStudentCard  — student list-item card
    KAFeeRow       — fee list row with colour-coded status
    KAActionButton — primary / secondary / danger action buttons
    KAEmptyState   — "nothing here" placeholder widget
    KASectionHeader — section title label
"""

from kivy.lang import Builder  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivymd.uix.button import MDRaisedButton, MDFlatButton  # type: ignore
from kivymd.uix.card import MDCard  # type: ignore
from kivymd.uix.label import MDLabel, MDIcon  # type: ignore

# ---------------------------------------------------------------------------
# Inline KV rules (Premium UI Updates)
# ---------------------------------------------------------------------------

Builder.load_string("""
#:import dp kivy.metrics.dp

<KACard>:
    radius: [dp(16), dp(16), dp(16), dp(16)]
    elevation: 1.5
    padding: dp(16)
    md_bg_color: 1, 1, 1, 1

<KAStatCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(110)
    radius: [dp(16), dp(16), dp(16), dp(16)]
    elevation: 1.5
    padding: dp(12)
    spacing: dp(4)
    md_bg_color: 1, 1, 1, 1
    ripple_behavior: True

<KAStudentCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(90)
    radius: [dp(12), dp(12), dp(12), dp(12)]
    elevation: 1.2
    padding: [dp(16), dp(12)]
    md_bg_color: 1, 1, 1, 1
    ripple_behavior: True

<KAFeeRow>:
    size_hint_y: None
    height: dp(60)
    radius: [dp(10), dp(10), dp(10), dp(10)]
    elevation: 1.2
    padding: [dp(16), dp(8)]
    md_bg_color: 1, 1, 1, 1
    ripple_behavior: True

<KAEmptyState>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(180)
    spacing: dp(10)

<KASectionHeader>:
    size_hint_y: None
    height: dp(40)
    bold: True
    theme_text_color: 'Custom'
    text_color: 0.247, 0.318, 0.710, 1  # Soft Indigo 500
    font_style: 'Subtitle1'
""")


# ---------------------------------------------------------------------------
# KACard
# ---------------------------------------------------------------------------

class KACard(MDCard):
    """A standard app card with rounded corners and a subtle shadow."""
    pass


# ---------------------------------------------------------------------------
# KAStatCard
# ---------------------------------------------------------------------------

class KAStatCard(MDCard):
    """
    A premium card for displaying a labelled statistic on the dashboard.
    Perfectly center-aligned with proper KivyMD icons.
    """

    def __init__(
        self,
        label: str = "",
        value: str = "0",
        icon: str = "information",
        icon_color: list = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if icon_color is None:
            icon_color = [0.0, 0.588, 0.533, 1]  # Teal Accent for Icons

        from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore

        # Main vertical container for perfect centering
        container = MDBoxLayout(orientation="vertical", spacing=dp(4))

        # Using MDIcon properly instead of raw text labels to prevent empty boxes
        icon_lbl = MDIcon(
            icon=icon,
            theme_text_color="Custom",
            text_color=icon_color,
            halign="center",
            font_size=dp(32),
            size_hint_y=None,
            height=dp(36)
        )
        
        val_lbl = MDLabel(
            text=str(value),
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=[0.247, 0.318, 0.710, 1],  # Soft Indigo
            halign="center",
            size_hint_y=None,
            height=dp(28)
        )
        
        lbl_lbl = MDLabel(
            text=label,
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
        )
        
        container.add_widget(icon_lbl)
        container.add_widget(val_lbl)
        container.add_widget(lbl_lbl)
        
        self.add_widget(container)
        self._val_lbl = val_lbl

    def update_value(self, new_value: str) -> None:
        """Change the displayed statistic value."""
        self._val_lbl.text = str(new_value)


# ---------------------------------------------------------------------------
# KAStudentCard
# ---------------------------------------------------------------------------

class KAStudentCard(MDCard):
    """
    A touch-enabled card representing a single student in a list.
    """

    def __init__(
        self,
        student: dict = None,
        on_tap=None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if student is None:
            student = {}
        self._student = student
        self._on_tap = on_tap

        from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore

        col = MDBoxLayout(orientation="vertical", spacing=dp(4))

        name_lbl = MDLabel(
            text=student.get("student_name", "Unknown"),
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(24),
        )
        father_lbl = MDLabel(
            text=f"S/O {student.get('father_name', '')}",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(18),
        )
        info_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(20))
        
        class_lbl = MDLabel(
            text=student.get("class_name", ""),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.247, 0.318, 0.710, 1], # Indigo
            size_hint_x=0.35,
        )
        phone_lbl = MDLabel(
            text=student.get("phone_number", ""),
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_x=0.35,
        )
        fee_lbl = MDLabel(
            text=f"Rs. {float(student.get('monthly_fee', 0)):,.0f}/mo",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.30, 0.69, 0.31, 1], # Soft Green
            size_hint_x=0.30,
            halign="right",
        )
        
        info_row.add_widget(class_lbl)
        info_row.add_widget(phone_lbl)
        info_row.add_widget(fee_lbl)

        col.add_widget(name_lbl)
        col.add_widget(father_lbl)
        col.add_widget(info_row)
        self.add_widget(col)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self._on_tap:
            self._on_tap(self._student)
        return super().on_touch_up(touch)


# ---------------------------------------------------------------------------
# KAFeeRow
# ---------------------------------------------------------------------------

STATUS_COLORS = {
    "Paid":    [0.30, 0.69, 0.31, 1],   # Soft Green
    "Unpaid":  [0.90, 0.32, 0.32, 1],   # Soft Red
    "Partial": [1.00, 0.60, 0.00, 1],   # Vibrant Orange
}

class KAFeeRow(MDCard):
    """
    A fee record row card with colour-coded payment status.
    """

    def __init__(self, fee: dict = None, on_tap=None, **kwargs) -> None:
        super().__init__(**kwargs)
        if fee is None:
            fee = {}
        self._fee = fee
        self._on_tap = on_tap

        from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
        from libs.utils import format_currency, format_month_year  # type: ignore

        row = MDBoxLayout(orientation="horizontal", spacing=dp(8))
        status = fee.get("status", "Unpaid")
        month_label = format_month_year(fee.get("month", ""))

        month_lbl = MDLabel(
            text=month_label,
            font_style="Body2",
            bold=True,
            theme_text_color="Primary",
            size_hint_x=0.30,
        )
        student_lbl = MDLabel(
            text=fee.get("student_name", ""),
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_x=0.28,
        )
        fee_lbl = MDLabel(
            text=format_currency(fee.get("fee_amount", 0)),
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_x=0.22,
            halign="right",
        )
        status_lbl = MDLabel(
            text=status,
            font_style="Body2",
            bold=True,
            theme_text_color="Custom",
            text_color=STATUS_COLORS.get(status, [0.90, 0.32, 0.32, 1]),
            size_hint_x=0.20,
            halign="center",
        )
        
        row.add_widget(month_lbl)
        row.add_widget(student_lbl)
        row.add_widget(fee_lbl)
        row.add_widget(status_lbl)
        self.add_widget(row)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self._on_tap:
            self._on_tap(self._fee)
        return super().on_touch_up(touch)


# ---------------------------------------------------------------------------
# KAActionButton helpers
# ---------------------------------------------------------------------------

def make_primary_button(text: str, on_release=None, **kwargs) -> MDRaisedButton:
    btn = MDRaisedButton(
        text=text,
        md_bg_color=[0.247, 0.318, 0.710, 1], # Indigo 500
        size_hint_x=kwargs.pop("size_hint_x", 1),
        height=dp(48),
        **kwargs,
    )
    if on_release:
        btn.bind(on_release=on_release)
    return btn


def make_secondary_button(text: str, on_release=None, **kwargs) -> MDFlatButton:
    btn = MDFlatButton(
        text=text,
        theme_text_color="Custom",
        text_color=[0.247, 0.318, 0.710, 1], # Indigo 500
        size_hint_x=kwargs.pop("size_hint_x", 1),
        height=dp(48),
        **kwargs,
    )
    if on_release:
        btn.bind(on_release=on_release)
    return btn


def make_danger_button(text: str, on_release=None, **kwargs) -> MDRaisedButton:
    btn = MDRaisedButton(
        text=text,
        md_bg_color=[0.898, 0.224, 0.208, 1], # Soft Red
        size_hint_x=kwargs.pop("size_hint_x", 1),
        height=dp(48),
        **kwargs,
    )
    if on_release:
        btn.bind(on_release=on_release)
    return btn


# ---------------------------------------------------------------------------
# KAEmptyState
# ---------------------------------------------------------------------------

class KAEmptyState(BoxLayout):
    """Centred empty-state placeholder with proper MDIcon."""

    def __init__(self, message: str = "No data found.", icon: str = "inbox", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(180)

        # Using MDIcon to prevent empty boxes
        icon_lbl = MDIcon(
            icon=icon,
            theme_text_color="Hint",
            halign="center",
            font_size=dp(64),
            size_hint_y=None,
            height=dp(80),
        )
        msg_lbl = MDLabel(
            text=message,
            font_style="Body1",
            theme_text_color="Hint",
            halign="center",
            size_hint_y=None,
            height=dp(40),
        )
        self.add_widget(icon_lbl)
        self.add_widget(msg_lbl)


# ---------------------------------------------------------------------------
# KASectionHeader
# ---------------------------------------------------------------------------

class KASectionHeader(MDLabel):
    """A bold section-title label styled in primary colour."""
    pass
