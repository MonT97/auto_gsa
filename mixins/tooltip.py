from tktooltip import ToolTip

class HasToolTip():
    def t_tip(self, widget, msg: str, font_size: int = 12, font_name: str = 'Arial') -> None:
        '''
        Adds a tooltip for the given [widget] using the provided [msg].
        '''
        ToolTip(widget,
            msg=msg,
            font=(font_name, font_size), fg='#ffffff', bg='#000000')