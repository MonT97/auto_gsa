"""
Consider a theme/styles module down the line.
"""
import customtkinter as ctk
import pywinstyles

def bg_transparent(widgets: ctk.CTkBaseClass|list[ctk.CTkBaseClass]) -> None:
    """
    Makes the [widget] background transparent.
    """
    _color: str = '#000001'

    if not isinstance(widgets, list):
        widgets  = [widgets]

    for widget in widgets:
        _id: int = widget.winfo_id()

        widget.configure(bg_color=_color)
        pywinstyles.set_opacity(_id, color=_color)