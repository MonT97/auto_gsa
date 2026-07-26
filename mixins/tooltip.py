from tkinter import Canvas

from customtkinter import CTkBaseClass
from tktooltip import ToolTip

# Constants
# colors:
FG_CLR = '#ffffff'
BG_CLR = '#000000'


class HasToolTip():
    """
    Adds a tooltip using the function: htt_tip().
    """
    def htt_tip(self, widget: CTkBaseClass|Canvas,
                msg: str, font_size: int = 12, font_name: str = 'Arial') -> None:
        """
        Part of the HasTooltip mixin.
        Adds a tooltip for the given [widget] using the provided [msg].
        """
        ToolTip(widget,
            msg=msg,
            font=(font_name, font_size), fg=FG_CLR, bg=BG_CLR)