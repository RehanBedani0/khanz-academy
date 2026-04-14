"""
Bottom navigation component for Khan'z Academy Mobile App.

Provides a BottomNavBar widget that can be embedded in any screen to give
persistent bottom-tab navigation between the four main sections.
"""

from kivy.metrics import dp  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.lang import Builder  # type: ignore
from kivy.app import App  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDFlatButton  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore

# ---------------------------------------------------------------------------
# KV rule for the nav bar container
# ---------------------------------------------------------------------------

Builder.load_string("""
#:import dp kivy.metrics.dp

<BottomNavBar>:
    size_hint_y: None
    height: dp(56)
    orientation: 'horizontal'
    md_bg_color: 0.10, 0.14, 0.49, 1
    elevation: 8
    padding: [dp(0), dp(0)]
    spacing: dp(0)
""")


# ---------------------------------------------------------------------------
# Tab definition
# ---------------------------------------------------------------------------

_NAV_TABS = [
    {"label": "Home",     "icon": "home",           "screen": "dashboard"},
    {"label": "Students", "icon": "account-group",  "screen": "view_students"},
    {"label": "Fees",     "icon": "cash",            "screen": "fee_management"},
    {"label": "Reports",  "icon": "chart-bar",       "screen": "reports"},
]


# ---------------------------------------------------------------------------
# BottomNavBar
# ---------------------------------------------------------------------------

class BottomNavBar(MDBoxLayout):
    """
    A horizontal bottom navigation bar with four fixed tabs.

    Usage::

        bar = BottomNavBar(active_screen='dashboard')
        parent.add_widget(bar)
    """

    def __init__(self, active_screen: str = "dashboard", **kwargs) -> None:
        super().__init__(**kwargs)
        self._active_screen = active_screen
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Create and add one button per navigation tab."""
        for tab in _NAV_TABS:
            btn = self._make_tab_button(tab)
            self.add_widget(btn)

    def _make_tab_button(self, tab: dict) -> MDFlatButton:
        """Return a styled flat button for a single navigation tab."""
        screen = tab["screen"]
        is_active = screen == self._active_screen

        text_color = (1, 1, 1, 1) if is_active else (0.75, 0.75, 1.0, 1)

        col = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            padding=[dp(4), dp(4)],
        )
        icon_lbl = MDLabel(
            text=tab["label"],
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=text_color,
            bold=is_active,
        )
        col.add_widget(icon_lbl)

        # Wrap in a touchable flat button
        btn = MDFlatButton(
            size_hint=(1, 1),
            theme_text_color="Custom",
            text_color=text_color,
        )
        btn.add_widget(col)
        btn.bind(on_release=lambda _b, s=screen: self._navigate(s))
        return btn

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _navigate(self, screen_name: str) -> None:
        """Ask the running App to switch to *screen_name*."""
        app = App.get_running_app()
        if app and hasattr(app, "go_to_screen"):
            app.go_to_screen(screen_name)
