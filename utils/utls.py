"""
Consider a theme/styles module down the line.
"""
from tkinter import BaseWidget, Toplevel
from typing import Callable

import customtkinter as ctk
import pandas as pd
import pywinstyles

# Constants:
# color:
TRANSPARENT_COLOR = '#000001'

def bg_transparent(widgets: ctk.CTkBaseClass|list[ctk.CTkBaseClass]) -> None:
    """
    Makes the [widget] background transparent.
    """

    if not isinstance(widgets, list):
        widgets  = [widgets]

    for widget in widgets:
        _id: int = widget.winfo_id()

        widget.configure(bg_color=TRANSPARENT_COLOR)
        pywinstyles.set_opacity(_id, color=TRANSPARENT_COLOR)

#! It's here due to circ import, when Sample import mixin, CanSave within mixin needs Sample and since Sample isn't fully initiated, CRASH!
def import_form_path(full_path: str, format_: str) -> pd.DataFrame:
        """
        Imports using the provided [full_path] and [format_] using the viable pd.read_[format_] function.\n
        Use for data validation without creating a Sample().
        - full_path: name inclusive.
        """
        _kw: dict[str, dict] = {'xlsx':{'engine':'openpyxl', 'header': None},
                'csv':{}}
        _fnc_dict: dict[str, Callable[[str], pd.DataFrame]] = {
                'csv': pd.read_csv,
                'xlsx': pd.read_excel
                }
        _read_fn: Callable[[str], pd.DataFrame] = lambda fmt:_fnc_dict[fmt](full_path, **_kw[fmt])
        _data: pd.DataFrame = _read_fn(format_)

        return _data

# this is only here because I dislike the type: ignore, as it's necessary in this case!
def get_root(widget: BaseWidget) -> Toplevel:
     """
     Returns the [widget]'s true root using [widget]._root().
     """
     return widget._root() #type: ignore