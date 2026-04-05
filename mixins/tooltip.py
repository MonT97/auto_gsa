from customtkinter import CTkBaseClass
from tktooltip import ToolTip

class HasToolTip():
    def htt_tip(self, widget: CTkBaseClass, msg: str, font_size: int = 12, font_name: str = 'Arial') -> None:
        '''
        Adds a tooltip for the given [widget] using the provided [msg].
        '''
        ToolTip(widget,
            msg=msg,
            font=(font_name, font_size), fg='#ffffff', bg='#000000')