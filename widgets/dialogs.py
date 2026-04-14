"""
Dialog and popup helpers for Khan'z Academy Mobile App.

All functions accept a parent widget and return / dismiss KivyMD dialogs.
Every function is safe to call from any screen.
"""

from typing import Callable, Optional

from kivy.clock import Clock  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.widget import Widget  # type: ignore
from kivymd.uix.button import MDFlatButton, MDRaisedButton  # type: ignore
from kivymd.uix.dialog import MDDialog  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivymd.uix.spinner import MDSpinner  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.graphics import Color, Rectangle  # type: ignore
from kivy.uix.floatlayout import FloatLayout  # type: ignore


# ---------------------------------------------------------------------------
# Internal: active loading overlay reference (singleton)
# ---------------------------------------------------------------------------

_active_loading_overlay: Optional[Widget] = None


# ---------------------------------------------------------------------------
# Colour constants
# ---------------------------------------------------------------------------

COLOR_ERROR_BG = [0.96, 0.26, 0.21, 1]     # Red
COLOR_SUCCESS_BG = [0.30, 0.69, 0.31, 1]   # Green
COLOR_INFO_BG = [0.13, 0.59, 0.95, 1]      # Blue
COLOR_WHITE_TEXT = [1, 1, 1, 1]


# ---------------------------------------------------------------------------
# Public dialog helpers
# ---------------------------------------------------------------------------

def show_error_dialog(title: str, message: str) -> MDDialog:
    """
    Display a modal error popup with a red-accented OK button.

    Returns the MDDialog instance (already opened).
    """
    dialog = MDDialog(
        title=f"[color=f44336]{title}[/color]",
        text=message,
        buttons=[
            MDRaisedButton(
                text="OK",
                md_bg_color=[0.96, 0.26, 0.21, 1],
                on_release=lambda _btn: dialog.dismiss(),
            )
        ],
    )
    dialog.open()
    return dialog


def show_success_dialog(title: str, message: str) -> MDDialog:
    """
    Display a modal success popup with a green-accented OK button.

    Returns the MDDialog instance (already opened).
    """
    dialog = MDDialog(
        title=f"[color=4caf50]{title}[/color]",
        text=message,
        buttons=[
            MDRaisedButton(
                text="OK",
                md_bg_color=[0.30, 0.69, 0.31, 1],
                on_release=lambda _btn: dialog.dismiss(),
            )
        ],
    )
    dialog.open()
    return dialog


def show_confirmation_dialog(
    title: str,
    message: str,
    on_confirm_callback: Callable,
) -> MDDialog:
    """
    Display a modal confirmation popup with CANCEL and CONFIRM buttons.

    The *on_confirm_callback* is called (with no arguments) only when the
    user taps CONFIRM.  Returns the MDDialog instance (already opened).
    """
    dialog_ref: list = []  # mutable container so inner lambda can close it

    def _on_confirm(_btn) -> None:
        if dialog_ref:
            dialog_ref[0].dismiss()
        on_confirm_callback()

    def _on_cancel(_btn) -> None:
        if dialog_ref:
            dialog_ref[0].dismiss()

    dialog = MDDialog(
        title=title,
        text=message,
        buttons=[
            MDFlatButton(
                text="CANCEL",
                theme_text_color="Custom",
                text_color=[0.13, 0.14, 0.49, 1],
                on_release=_on_cancel,
            ),
            MDRaisedButton(
                text="CONFIRM",
                md_bg_color=[0.96, 0.26, 0.21, 1],
                on_release=_on_confirm,
            ),
        ],
    )
    dialog_ref.append(dialog)
    dialog.open()
    return dialog


def show_info_dialog(title: str, message: str) -> MDDialog:
    """
    Display a modal informational popup with a blue-accented OK button.

    Returns the MDDialog instance (already opened).
    """
    dialog = MDDialog(
        title=f"[color=1565c0]{title}[/color]",
        text=message,
        buttons=[
            MDRaisedButton(
                text="OK",
                md_bg_color=[0.13, 0.59, 0.95, 1],
                on_release=lambda _btn: dialog.dismiss(),
            )
        ],
    )
    dialog.open()
    return dialog


# ---------------------------------------------------------------------------
# Loading indicator
# ---------------------------------------------------------------------------

class _LoadingOverlay(FloatLayout):
    """
    A semi-transparent overlay with a centred Material spinner.

    Added directly to the running App's root widget.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # Semi-transparent dark background
        with self.canvas.before:
            Color(0, 0, 0, 0.45)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            active=True,
            color=[0.13, 0.14, 0.49, 1],
        )
        self.add_widget(spinner)

    def _update_bg(self, *_args) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


def show_loading_indicator() -> None:
    """Add a full-screen loading spinner overlay to the running app's root."""
    global _active_loading_overlay

    from kivy.app import App  # local import avoids circular dependency

    app = App.get_running_app()
    if app is None or app.root is None:
        return
    if _active_loading_overlay is not None:
        return  # already shown

    overlay = _LoadingOverlay()
    app.root.add_widget(overlay)
    _active_loading_overlay = overlay


def dismiss_loading_indicator() -> None:
    """Remove the loading spinner overlay if it is currently displayed."""
    global _active_loading_overlay

    from kivy.app import App

    app = App.get_running_app()
    if _active_loading_overlay is None:
        return
    if app is not None and app.root is not None:
        try:
            app.root.remove_widget(_active_loading_overlay)
        except Exception:
            pass
    _active_loading_overlay = None
