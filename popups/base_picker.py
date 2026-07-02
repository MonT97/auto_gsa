"""
The Base class for the various pickers in pickers.py.
"""
from mixins import HasToolTip

import customtkinter as ctk

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
        self.entry.configure(state=ctk.DISABLED, border_color='#565b5e')

        self.toggle.pack(side='left', padx=2)
        self.entry.pack(side='left', fill='x', expand=True, padx=2)
    
    def _activation(self) -> None:
        """
        Enables/Disables the widget.
        """
        _enabled = bool(self.toggle.get())
        
        if _enabled:
            self.entry.configure(state=ctk.NORMAL, border_color='#7a848d')
            self.entry.configure(placeholder_text='')
            self.after(1, self.entry.focus_set)
        else:
            self.entry.configure(placeholder_text=self.val)
            self.entry.configure(state=ctk.DISABLED, border_color='#565b5e')
    
    def _on_mouse_enter(self) -> None:
        """
        When the mouse enters the entry widget.
        """
        if self.toggle.get():
            self.after(1,self.entry.focus_set)
            self.entry.select_to(ctk.END)

    def _validate(self) -> None:
        """
        Validates user input, each child implements his own.
        """
        pass

    def _update_value(self, value: str) -> None:
        """
        Udates whats written in the entry widget using the given [value].
        """
        self.entry.delete(0, ctk.END)
        self.entry.insert(0, value)

    def get_value(self) -> str:
        """
        Returns the value.
        """
        _value = self.entry.get()
        return _value if _value else self.val