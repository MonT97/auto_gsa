"""
The Base class for the various pickers in pickers.py.
"""
import customtkinter as ctk

from mixins import HasToolTip
from utils import utls

# Constants
# colors:
ACTIVE_ENTRY_CLR = '#ffffff'
DEFAULT_ENTRY_CLR = '#565b5e'

#TODO: find a better way to handle defaults.
class BasePicker(ctk.CTkFrame, HasToolTip):
    """
    The base picker class:
    - widgets:
        - check_box: ctk.CheckBox -> for en/disabling the entry field.
        - entry: ctk.Entry -> for data entry.
    """
    def __init__(self, master,
                label_txt: str, default_value: str,
                tooltip_msg: str = '') -> None:
        super().__init__(master)
        """
        - Prams:
            - label_txt: the toggle's label.
            - default_value: the default value, placeholder text.
            - tooltip_msg: the text to be shown in the tool tip.
        """
        self.val = default_value
        
        self.toggle = ctk.CTkSwitch(self,
                    text=label_txt, width= 150, command=lambda: self._activation())
        if tooltip_msg:
            self.htt_tip(self.toggle, tooltip_msg)

        self.entry = ctk.CTkEntry(self, placeholder_text=default_value)
        self.entry.bind('<Enter>', lambda _: self._on_mouse_enter())
        self.entry.bind('<FocusOut>', lambda _: self._validate())
        utls.bg_transparent(self.entry)
        self.entry.configure(state=ctk.DISABLED, border_color=DEFAULT_ENTRY_CLR)

        self.toggle.pack(side='left', padx=2)
        self.entry.pack(side='left', fill='x', expand=True, padx=2, pady=2)
    
    def _activation(self) -> None:
        """
        Enables/Disables the widget.
        """
        _enabled = bool(self.toggle.get())
        
        if _enabled:
            self.entry.configure(state=ctk.NORMAL, border_color=ACTIVE_ENTRY_CLR)
            self.after(1, self.entry.focus_set)
            self.entry.select_to(ctk.END)
        else:
            self.entry.configure(placeholder_text=self.val)
            self.entry.configure(state=ctk.DISABLED, border_color=DEFAULT_ENTRY_CLR)
    
    def _on_mouse_enter(self) -> None:
        """
        When the mouse enters the entry widget.
        """
        if self.toggle.get():
            self.after(1,self.entry.focus_set)
            self.entry.select_to(ctk.END)

    def _validate(self) -> None:
        """
        Validates user input, each instance implements his own.
        """
        pass

    def _update_value(self, value: str) -> None:
        """
        Udates whats written in the entry widget using the given [value].
        """
        self.entry.delete(0, ctk.END)
        self.entry.insert(0, value)

    def update_default(self, value: str) -> None:
        """
        Updates the placeholder_text and the self.val using [value].
        """
        self.val = value
        self.toggle.toggle()
        self.toggle.toggle()

    def get_value(self) -> str:
        """
        Returns the value.
        """
        _value = self.entry.get()
        return _value if _value else self.val


class BaseToggle(ctk.CTkFrame, HasToolTip):
    """
    Picking whether to save the raw file or not.
    """
    def __init__(self, master, label_text: str, tooltip_msg: str = '') -> None:
        super().__init__(master)

        self.toggle: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
                    text=label_text, border_width=2,
                    checkbox_height=20, checkbox_width=20)

        if tooltip_msg:
            self.htt_tip(self.toggle, tooltip_msg)
        
        utls.bg_transparent([self.toggle])
        self.toggle.pack(side='left', padx=2)

    def get_value(self) -> bool:
        """
        Returns the color.
        """
        return bool(self.toggle.get())