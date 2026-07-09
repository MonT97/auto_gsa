"""
ExportScreen inputs manipulation.
"""
import re
from collections.abc import Callable

import customtkinter as ctk

from mixins import HasToolTip
from shared_widgets import ColorPicker

from .base_picker import BasePicker, BaseToggle # needed for export_screen


class DpiPicker(BasePicker):
    """
    Picking the DPI, density per inch, i.e. resolution.
    """
    def __init__(self, master, label_txt: str, default_value: str, tooltip_msg: str = '') -> None:
        """
        Picking the DPI, density per inch, i.e. resolution.
        """
        super().__init__(master, label_txt, default_value, tooltip_msg)

    def _validate(self) -> None:
        """
        Limits and validates the dpi value.
        """
        _min = 50
        _max = 600
        _dpi = re.findall(r'([0-9]+)', self.get_value())
        _dpi = _min if not _dpi else max(min(int(_dpi[0]), _max), _min)
        self._update_value(str(_dpi))


class IntervalPicker(ctk.CTkFrame, HasToolTip):
    """
    Picking the interval, which files to save.
    """
    def __init__(self, master) -> None:
        """
        Picking the interval, which files to save.
        """
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
                self.htt_tip(self.u_limit_entry, 'The start of the interval, enclusive.')
                self.u_limit_entry.bind("<FocusOut>",
                    lambda _: self._validate_input(self.u_var, 'u'))

                self.l_limit_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                        width=40, textvariable=self.l_var)
                self.htt_tip(self.l_limit_entry, 'The end of the interval, enclusive.')
                self.l_limit_entry.bind("<FocusOut>",
                    lambda _: self._validate_input(self.l_var, 'l'))

                self.u_limit_entry.place(anchor='w', relx=0+_padding, rely=.5)
                self.to.place(anchor='n', relx=.5, rely=0)
                self.l_limit_entry.place(anchor='e', relx=1-_padding, rely=.5)

            def _validate_input(self, var: ctk.StringVar, limit: str) -> None:
                """
                Input validation.
                """
                _val: str = var.get()

                _val_is_valid: Callable = lambda x: bool(re.match('^-[0-9]+$|^[0-9]+$', x))
                
                if _val_is_valid(_val):
                    var.set(f'{max(int(_val), 0)}') if limit == 'u' else var.set(f'{min(int(_val), self.u_lim)}')
                    return

                var.set('')

            def _get_var(self) -> str:

                _u_lim: int = int(self.u_var.get())
                _l_lim: int = int(self.l_var.get())+1 #for the exclusivity of python list indexing

                return f'{_u_lim},{_l_lim}'


        class ListPckr(ctk.CTkFrame, HasToolTip):

            def __init__(self, master) -> None:
                super().__init__(master)

                self.u_lim: int = 0 # set from master
                self.variable: ctk.StringVar = ctk.StringVar(self)
                
                self.list_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                            textvariable=self.variable)
                self.htt_tip(self.list_entry, 'List of sample numbers, for example:\n- [1,2,6]: chooses samples 1, 2 and 6.\n- use only [,]as a delimiter.')
                self.list_entry.bind("<FocusOut>", lambda _: self._validate_input(self.variable))

                self.list_entry.pack()
            
            def _validate_input(self, value: ctk.StringVar) -> None:
                """
                Input validation.
                """
                _value: str = value.get()

                _numbers: list[str] = re.findall(r'[0-9]+', _value)

                _cap_number: Callable = lambda x: f'{min(int(x), self.u_lim)}'
                _str_numbers: str = ','.join([_cap_number(i) for i in _numbers])

                value.set(_str_numbers)

            def _get_var(self) -> str:

                return self.variable.get()

        _options: list[str] = ['all', 'interval', 'list']

        self.getter_function: Callable[[],str]
        self.pick_var: ctk.StringVar = ctk.StringVar(self, value=_options[0])

        self.label: ctk.CTkLabel = ctk.CTkLabel(self,
                    anchor='w', text='Selection method:', height=17)
        self.htt_tip(self.label, 'The method used to scelect samples to export.')

        self.drop_down: ctk.CTkComboBox = ctk.CTkComboBox(self,
                    values=_options, variable=self.pick_var,
                    command=lambda _: self._update_layout(_))

        self.interval_pckr: IntPckr = IntPckr(self)
        self.list_pckr: ListPckr = ListPckr(self)

        self.label.pack(side='top', fill='x', padx=2)
        self._update_layout(_options[0])

    def _update_layout(self, option: str) -> None:

        for i in self.winfo_children()[1:]:
            i.pack_forget()

        match option:
            case 'all':
                self.drop_down.pack(side='left', expand=True, fill='x', padx=2, pady=2)
                self.index = 0
            case 'interval':
                self.drop_down.pack(side='left', fill='x', padx=2, pady=2)
                self.interval_pckr.pack(side='top', fill='x', padx=2, pady=2)
                self._set_getter(self.interval_pckr)
                self.index = 1
            case 'list':
                self.drop_down.pack(side='left', fill='x', padx=2, pady=2)
                self.list_pckr.pack(side='left', fill='x', padx=2, pady=2, expand=True)
                self._set_getter(self.list_pckr)
                self.index = 2

    def _set_getter(self, widget) -> None:
        """
        Sets the getter function based on child widget picked.
        """
        self.getter_function = widget._get_var
    
    def set_upper_limit(self, val: int) -> None:
        """
        Tells the widget how many samples there is.
        """
        self.interval_pckr.u_lim = val
        self.list_pckr.u_lim = val

    def get_value(self) -> tuple[int,list[int|None]]:
        """
        Returns the parameter
        """
        _output = []
        
        if self.index != 0:
            _output: list[int|None] = [int(i)-1 for i in self.getter_function().split(',')]
        
        return  (self.index, _output)
    

class GraphColorPicker(ctk.CTkFrame):
    """
    Picking the color of the exported graphs/plots.
    """
    def __init__(self, master) -> None:
        super().__init__(master)

        self.color: str = ''

        self.toggle: ctk.CTkSwitch = ctk.CTkSwitch(self,
            text='Use preview color', width=150,
            command=lambda: self._on_check())
        self.color_pckr: ColorPicker = ColorPicker(self)
        self.toggle.toggle()

        self.toggle.pack(side='left')

    def _on_check(self) -> None:
 
        if self.toggle.get():
            self.color_pckr.pack_forget()
            self.toggle.configure(text='Use preview color')
        else:
            self.toggle.configure(text='Pick a color')
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
    

# class SaveRawsPicker(ctk.CTkFrame, HasToolTip):
#     """
#     Picking whether to save the raw file or not.
#     """
#     def __init__(self, master, label_text: str, tooltip_msg: str = '') -> None:
#         super().__init__(master)
#         self.toggle: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
#                     text=label_text, border_width=2,
#                     checkbox_height=20, checkbox_width=20)

#         if tooltip_msg:
#             self.htt_tip(self.toggle, tooltip_msg)
        
#         utls.bg_transparent([self.toggle])
#         self.toggle.pack(side='left', padx=2)

#     def get_value(self) -> bool:
#         """
#         Returns the color.
#         """
#         return bool(self.toggle.get())


# class TransparencyPicker(ctk.CTkFrame, HasToolTip):
#     """
#     Picking whether to save the raw file or not.
#     """
#     def __init__(self, master, label_text: str, tooltip_msg: str = '') -> None:
#         super().__init__(master)
#         self.toggle: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
#                     text=label_text, border_width=2,
#                     checkbox_height=20, checkbox_width=20)

#         if tooltip_msg:
#             self.htt_tip(self.toggle, tooltip_msg)
        
#         utls.bg_transparent([self.toggle])
#         self.toggle.pack(side='left', padx=2)

#     def get_value(self) -> bool:
#         """
#         Returns the color.
#         """
#         return bool(self.toggle.get())