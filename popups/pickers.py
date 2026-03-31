"""
Save inputs manipulation.
"""
from collections.abc import Callable

from shared_widgets import ColorPicker
from mixins import HasToolTip

import customtkinter as ctk

#TODO: find a better way to handle defaults.
class BasePicker(ctk.CTkFrame, HasToolTip):
    """
    The base picker class:
    - widgets:
        - check_box: ctk.CheckBox -> for en/disabling the entry field.
        - entry: ctk.Entry -> for data entry.
    - Prams:
        - label_txt: the check_box's label.
        - default_value: the default value
    """
    def __init__(self, master, label_txt: str, default_value: str, tooltip_msg: str = '') -> None:
        super().__init__(master)
        self.val = default_value
        
        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
                    text=label_txt, checkbox_height=20, checkbox_width=20,
                    width= 150, command=lambda: self._activation())
        if tooltip_msg:
            self.t_tip(self.check_box, tooltip_msg)

        self.entry: ctk.CTkEntry = ctk.CTkEntry(self, placeholder_text=default_value)
        self.entry.configure(state=ctk.DISABLED, border_color='#565b5e')

        self.check_box.pack(side='left')
        self.entry.pack(side='left', fill='x', expand=True)
    
    def _activation(self) -> None:
        """
        Enables/Disables the widget.
        """
        _enabled: bool = bool(self.check_box.get())
        
        if _enabled:
            self.entry.configure(state=ctk.NORMAL, border_color='#7a848d')
            self.entry.configure(placeholder_text='')
            self.entry.focus_set()
        else:
            self.entry.configure(placeholder_text=self.val)
            self.entry.configure(state=ctk.DISABLED, border_color='#565b5e')
    
    def get_value(self) -> str:
        """
        Returns the value.
        """
        _value = self.entry.get()
        return _value if _value else self.val


class IntervalPicker(ctk.CTkFrame, HasToolTip):
    """
    Picking the interval, which files to save.
    """
    def __init__(self, master) -> None:
        super().__init__(master)

        class IntPckr(ctk.CTkFrame, HasToolTip):

            def __init__(self, master):
                super().__init__(master)

                _padding: float = .2
                self.u_lim: int = 0 # set from master
                self.configure(height=28)

                self.u_var: ctk.StringVar = ctk.StringVar(self)
                self.l_var: ctk.StringVar = ctk.StringVar(self)

                self.to: ctk.CTkLabel = ctk.CTkLabel(self, text='to')
           
                self.u_limit_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                        width=40, textvariable=self.u_var)
                self.t_tip(self.u_limit_entry, 'The start of the interval, enclusive.')
                self.u_limit_entry.bind("<FocusOut>",
                    lambda _: self._validate_input(self.u_var, 'u'))

                self.l_limit_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                        width=40, textvariable=self.l_var)
                self.t_tip(self.l_limit_entry, 'The end of the interval, enclusive.')
                self.l_limit_entry.bind("<FocusOut>",
                    lambda _: self._validate_input(self.l_var, 'l'))

                self.u_limit_entry.place(anchor='w', relx=0+_padding, rely=.5)
                self.to.place(anchor='n', relx=.5, rely=0)
                self.l_limit_entry.place(anchor='e', relx=1-_padding, rely=.5)

            def _validate_input(self, var: ctk.StringVar, limit: str) -> None:
                
                _val: str = var.get()

                if _val.isnumeric():
                    var.set(f'{max(int(_val), 0)}') if limit == 'u' else var.set(f'{min(int(_val), self.u_lim)}')
                    return

                var.set('') if limit == 'u' else var.set('')

            def get_var(self) -> str:

                _u_lim: int = int(self.u_var.get())
                _l_lim: int = int(self.l_var.get())+1
                return f'{_u_lim}+{_l_lim}'


        class ListPckr(ctk.CTkFrame):

            def __init__(self, master) -> None:
                super().__init__(master)

                self.list_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                            placeholder_text='1, 2, 3, ...')

                self.list_entry.pack()
            
            def get_var(self) -> str:

                return self.list_entry.get()

        _options: list[str] = ['all', 'interval', 'list']

        self.getter_function: Callable[[],str]
        self.pick_var: ctk.StringVar = ctk.StringVar(self, value=_options[0])

        self.drop_down: ctk.CTkComboBox = ctk.CTkComboBox(self,
                    values=_options, variable=self.pick_var,
                    command=lambda _: self._update_layout(_))

        self.interval_pckr: IntPckr = IntPckr(self)
        self.list_pckr: ListPckr = ListPckr(self)

        self._update_layout(_options[0])

    def _update_layout(self, option: str) -> None:

        for i in self.winfo_children():
            i.pack_forget()

        match option:
            case 'all':
                self.drop_down.pack(side='left', expand=True, fill='x')
                self.index = 0
            case 'interval':
                self.drop_down.pack(side='left', fill='x')
                self.interval_pckr.pack(side='top', fill='x', padx=2, pady=2)
                self.set_getter(self.interval_pckr)
                self.index = 1
            case 'list':
                self.drop_down.pack(side='left', fill='x')
                self.list_pckr.pack(side='left', fill='x', padx=2, pady=2, expand=True)
                self.set_getter(self.list_pckr)
                self.index = 2
    
    def set_upper_limit(self, val: int) -> None:

        self.interval_pckr.u_lim = val

    def set_getter(self, widget) -> None:
        """
        Sets the getter function based on child widget picked.
        """
        self.getter_function = widget.get_var

    def get_value(self) -> tuple[int,list[int|None]]:
        """
        Returns the parameter
        """
        _output = []

        if self.index != 0:
            _output: list[int|None] = [int(i)-1 for i in self.getter_function() if i.isnumeric()]

        return  (self.index, _output)
    

class GraphColorPicker(ctk.CTkFrame):
    """
    Picking the paths to house the results within.
    """
    def __init__(self, master) -> None:
        super().__init__(master)

        self.color: str = ''

        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
            text='Use preview color', width=150,
            checkbox_height=20, checkbox_width=20,
            command=lambda: self._on_check())
        self.color_pckr: ColorPicker = ColorPicker(self)
        self.check_box.toggle()

        self.check_box.pack(side='left')

    def _on_check(self) -> None:
 
        if self.check_box.get():
            self.color_pckr.pack_forget()
            self.check_box.configure(text='Use preview color')
        else:
            self.check_box.configure(text='Pick a color')
            self.color_pckr.pack(side='top', padx=2, pady=2)

    def on_preview_press(self, color: str) -> None:
        """
        Triggerd by a preview button press From the clr_pikr: ColorPicker.
        """
        self.color = color

    def get_value(self) -> str:
        """
        Returns the color.
        """
        return self.color
    

class SaveRawsPicker(ctk.CTkFrame, HasToolTip):
    """
    Picking whether to save the raw file or not.
    """
    def __init__(self, master, tooltip_msg: str = '') -> None:
        super().__init__(master)
        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
            text='Save raw files', checkbox_height=20, checkbox_width=20)
        if tooltip_msg:
            self.t_tip(self.check_box, tooltip_msg)
        self.check_box.pack(side='left')
        self.check_box.toggle()

    def get_value(self) -> bool:
        """
        Returns the color.
        """
        return bool(self.check_box.get())