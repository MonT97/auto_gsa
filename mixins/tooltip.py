from tkinter import Widget
from typing import Literal

from tktooltip import ToolTip

# Constants
# colors:
FG_CLR = '#ffffff'
BG_CLR = '#000000'

FW = Literal['normal', 'bold']

class HasToolTip():
    """
    Adds a tooltip using the function:
    - `htt_tip`: adds a tooltip for a function.
    """
    _ttip_dict: dict[Widget|str,tuple[str,ToolTip]] = {}
    
    def htt_tip(self, widget: Widget,
                msg: str, delay: float = .75, font_size: int = 12,
                font_family_name: str = 'Arial', font_weight: FW = 'normal', id_: str = '', kw={}) -> ToolTip:
        """
        Part of the HasTooltip mixin.
        Adds a tooltip for the given [widget] using the provided [msg].
        - `delay`: in seconds.
        - `kw`: a typical **kw to pass to ToolTip super() tk.Massage.
        """
        # Something wrecks the tooltip when the [widget] is cached, hence, this if statement:
        if id_ and id_ in self._ttip_dict:
            _ttip = self._ttip_dict.pop(id_)[-1]
            _ttip.destroy()

        elif widget in self._ttip_dict:
            _ttip = self._ttip_dict.pop(widget)[-1]
            _ttip.destroy()

        ttip = ToolTip(widget, msg=msg, font=(font_family_name, font_size, font_weight),
                fg=FG_CLR, bg=BG_CLR, delay=delay, **kw)
        
        if id_:
            self._ttip_dict[id_] = (msg, ttip)
            return ttip
        self._ttip_dict[widget] = (msg, ttip)

        return ttip
