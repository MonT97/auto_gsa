"""
ExportScreen inputs manipulation.
"""
import os
import re
from collections.abc import Callable
from PIL import Image
from typing import Final, Literal

import customtkinter as ctk

from mixins import HasToolTip, Observer
from shared_widgets import ColorPicker
from typedefs import Signal

from .base_picker import BasePicker  # needed for export_screen
from .base_screen import DirPickScreen

# Constants:
# color
ACTIVE_ENTRY_CLR: Final[str] = '#ffffff'
DEFAULT_ENTRY_CLR: Final[str] = '#565b5e'
ACTIVE_TXT_CLR: Final[str] = '#dce4ee'
DISABLED_TXT_CLR: Final[str] = '#9e9e9e'

# icons
ICON_SIZE: Final[tuple[int,int]] = (20,20)
IMPORT_ICON: Final = Image.open(r'assets\folder_b.png')
DIS_IMPORT_ICON: Final = Image.open(r'assets\folder_b_dis.png')

LIMIT = Literal['u', 'l']

class DirPicker(ctk.CTkFrame, HasToolTip):
    """
    Directory picker dialog.
    - `functions`:
    - `get_path`: returns the path.
    - `get_name`: get the name of the file.
    """
    def __init__(self, master, label_txt: str, full_path: str, tooltip_msg: str = '') -> None:
        """
        Directory picker dialog.
        - label_txt: the toggle's label.
        - full_path: the default value.
        - tooltip_msg: the text to be shown in the tool tip.
        """
        super().__init__(master)
        self._tip_msg: str = '[Enter/Return]x2: open import screen'
        self._full_path: str = full_path
        self._master = master.master

        self._dir_screen = DirPickScreen(self, self._full_path)
        self._toggle = ctk.CTkSwitch(self,
                    text=label_txt, width= 150, command=lambda: self._activation())
        if tooltip_msg:
            self.htt_tip(self._toggle, tooltip_msg)

        self._entry = ctk.CTkEntry(self, state=ctk.DISABLED)
        self._entry.set(full_path)
        self._entry.bind('<FocusIn>', lambda _: self._update_tip_and_scroll())
        self._entry.bind('<KeyPress-Return>', lambda _: self._update_full_path())
        self._entry.bind('<FocusOut>', lambda _: self._update_full_path(reset=True))
        self._entry.bind('<KeyPress-Escape>', lambda _: self._update_full_path(reset=True))
        self._entry.bind('<Double-KeyPress-Return>', lambda _: self._open_import_screen())
        self._update_tip_and_scroll()
        self._entry.configure(border_color=DEFAULT_ENTRY_CLR, text_color=DISABLED_TXT_CLR)

        self._import_icon = ctk.CTkImage(IMPORT_ICON, size=ICON_SIZE)
        self._dis_import_icon = ctk.CTkImage(DIS_IMPORT_ICON, size=ICON_SIZE)

        self._import_btn = ctk.CTkButton(self, text='', image=self._dis_import_icon,
                    command=lambda: self._open_import_screen(), width=15)
        self._import_btn.configure(state=ctk.DISABLED)
        self.htt_tip(self._import_btn, 'browse for folders')

        self._toggle.pack(side='left', padx=2)
        self._entry.pack(side='left', fill='x', expand=True, padx=(2,0), pady=2)
        self._import_btn.pack(side='left', fill='x', expand=False, padx=2, pady=2)
    
    def _activation(self) -> None:
        """
        Enables/Disables the widget.
        """
        _enabled = bool(self._toggle.get())
        
        if _enabled:
            self._entry.configure(state=ctk.NORMAL,
                        border_color=ACTIVE_ENTRY_CLR, text_color=ACTIVE_TXT_CLR)
            self._import_btn.configure(state=ctk.NORMAL, image=self._import_icon)
            self.after(1, self._entry.focus_set)
            self._entry.select_range(0, ctk.END)
        else:
            self._entry.configure(state=ctk.DISABLED, 
                        border_color=DEFAULT_ENTRY_CLR, text_color=DISABLED_TXT_CLR)
            self._import_btn.configure(state=ctk.DISABLED, image=self._dis_import_icon)
    
    def _update_tip_and_scroll(self) -> None:
        """
        Scrolls to the [self._entry] widget to the end of the text and updates the [tooltip].
        """
        _scroll_unit: int = len(self._full_path)
        self._entry.xview_scroll(_scroll_unit,'units')
        self._entry.select_range(0, ctk.END)
        self.htt_tip(self._entry, self._tip_msg+f'\npath: {self._full_path}')

    def _update_full_path(self, reset: bool = False) -> None:
        if not os.path.exists(self._entry.get()) or reset:
            self._entry.set(self._full_path)
            return
        self._full_path = self._entry.get()
        self._update_tip_and_scroll()

    def _open_import_screen(self) -> None:
        """
        When the mouse enters the entry widget.
        """
        if self._toggle.get():
            self._master.attributes('-topmost', False)
            _full_path = self._dir_screen.show(self._full_path)
            if _full_path:
                self._full_path = _full_path
                self._entry.set(self._full_path)
                self._update_tip_and_scroll()
            self._master.attributes('-topmost', True)

    def get_path(self) -> str:
        """
        Returns the path.
        """
        return os.path.split(self._full_path)[0]
    
    def get_dir_name(self) -> str:
        """
        Returns the directory/folder name.
        """
        return os.path.split(self._full_path)[-1]


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
    def __init__(self, master, default_interval: tuple[int,list[int]] = (0,[])) -> None:
        """
        Picking the interval, which files to save.
        - default_interval: determines the launch state of the widget.
        """
        super().__init__(master)

        class IntPckr(ctk.CTkFrame, HasToolTip):

            def __init__(self, master):
                super().__init__(master)
                _padding: float = .2

                self._u_lim: int = 0 # set from master
                self.configure(height=28)

                self._u_var: ctk.StringVar = ctk.StringVar(self)
                self._l_var: ctk.StringVar = ctk.StringVar(self)
                
                self._to: ctk.CTkLabel = ctk.CTkLabel(self, text='to')
           
                self._u_limit_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                        width=40, textvariable=self._u_var, border_color=ACTIVE_ENTRY_CLR)
                self.htt_tip(self._u_limit_entry, 'The start of the interval, enclusive.')
                self._u_limit_entry.bind("<FocusOut>",
                    lambda _: self._validate_input(self._u_var, 'u'))
                self._u_limit_entry.bind('<Enter>',
                                        lambda _: self._on_mouse_enter(self._u_limit_entry))

                self._l_limit_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                        width=40, textvariable=self._l_var, border_color=ACTIVE_ENTRY_CLR)
                self.htt_tip(self._l_limit_entry, 'The end of the interval, enclusive.')
                self._l_limit_entry.bind("<FocusOut>",
                    lambda _: self._validate_input(self._l_var, 'l'))
                self._l_limit_entry.bind('<Enter>',
                                        lambda _: self._on_mouse_enter(self._l_limit_entry))

                self._u_limit_entry.place(anchor='w', relx=0+_padding, rely=.5)
                self._to.place(anchor='n', relx=.5, rely=0)
                self._l_limit_entry.place(anchor='e', relx=1-_padding, rely=.5)

                # if the SaveObj in export screen has these values:
                if self._u_var.get() and self._l_var.get():
                    self._validate_input(self._u_var, 'u')
                    self._validate_input(self._l_var, 'l')

            def _on_mouse_enter(self, entry: ctk.CTkEntry) -> None:
                """
                When the mouse enters the entry widget.
                """
                self.after(1,entry.focus_set)
                entry.select_range('0', ctk.END)

            def _validate_input(self, var: ctk.StringVar, limit: LIMIT) -> None:
                """
                Input validation.
                """
                _val: str = var.get()

                _val_is_valid: Callable = lambda x: bool(re.match('^-[0-9]+$|^[0-9]+$', x))
                
                if _val_is_valid(_val):
                    var.set(f'{max(int(_val), 0)}') if limit == 'u' else var.set(f'{min(int(_val), self._u_lim)}')
                    return

                var.set('')

            def get_var(self) -> str:

                _u_lim: int = int(self._u_var.get())
                _l_lim: int = int(self._l_var.get())+1 #for the exclusivity of python list indexing

                return f'{_u_lim},{_l_lim}'
            
            def set_var(self, interval: list[int]) -> None:
                """
                Sets the var before viewing the widget.
                """
                _u, _l = interval if len(interval) == 2 else [-1,0]
                self._u_var.set(value=str(_u+1))
                self._l_var.set(value=str(_l))


        class ListPckr(ctk.CTkFrame, HasToolTip):

            def __init__(self, master) -> None:
                super().__init__(master)

                self._u_lim: int = 0 # set from master
                self._variable: ctk.StringVar = ctk.StringVar(self)

                self._list_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                            textvariable=self._variable, border_color=ACTIVE_ENTRY_CLR)
                self.htt_tip(self._list_entry, 'List of sample numbers, for example:\n- [1,2,6]: chooses samples 1, 2 and 6.\n- use only [,]as a delimiter.')
                self._list_entry.bind('<Enter>', lambda _: self._on_mouse_enter())
                self._list_entry.bind("<FocusOut>", lambda _: self._validate_input(self._variable))

                # if the SaveObj in export screen has this value
                if self._variable.get():
                    self._validate_input(self._variable)

                self._list_entry.pack()
            
            def _on_mouse_enter(self) -> None:
                """
                When the mouse enters the entry widget.
                """
                self.after(1,self._list_entry.focus_set)
                self._list_entry.select_range('0', ctk.END)

            def _validate_input(self, value: ctk.StringVar) -> None:
                """
                Input validation.
                """
                _value: str = value.get()

                _numbers: list[str] = re.findall(r'[0-9]+', _value)

                _cap_number: Callable = lambda x: f'{min(int(x), self._u_lim)}'
                _str_numbers: str = ','.join([_cap_number(i) for i in _numbers])

                value.set(_str_numbers)

            def get_var(self) -> str:

                return self._variable.get()

            def set_var(self, interval: list[int]) -> None:
                """
                Sets the var before viewing the widget.
                """
                _interv = ','.join(f'{i+1}' for i in interval)
                self._variable.set(_interv)

        self._index: int = 0
        _options: list[str] = ['all', 'interval', 'list']
        self._index, self._interv = default_interval

        self._getter_function: Callable[[],str]
        self._pick_var: ctk.StringVar = ctk.StringVar(self, value=_options[self._index])

        self._label: ctk.CTkLabel = ctk.CTkLabel(self,
                    anchor='w', text='Selection method:', height=17)
        self.htt_tip(self._label, 'The method used to select samples to export.')

        self._drop_down: ctk.CTkComboBox = ctk.CTkComboBox(self,
                    values=_options, variable=self._pick_var, state='readonly',
                    command=lambda _: self._update_layout(_))

        self._interval_pckr: IntPckr = IntPckr(self)
        self._list_pckr: ListPckr = ListPckr(self)

        self._label.pack(side='top', fill='x', padx=2)
        self._update_layout(_options[self._index])

    def _update_layout(self, option: str) -> None:
        """
        Updates the layout based on [option].
        """
        for i in self.winfo_children()[1:]:
            i.pack_forget()

        match option:
            case 'all':
                self._drop_down.pack(side='left', expand=True, fill='x', padx=2, pady=2)
                self._index = 0
            case 'interval':
                self._drop_down.pack(side='left', fill='x', padx=2, pady=2)
                self._interval_pckr.pack(side='top', fill='x', padx=2, pady=2)
                if self._interv:
                    self._interval_pckr.set_var(self._interv)
                self._set_getter(self._interval_pckr)
                self._index = 1
            case 'list':
                self._drop_down.pack(side='left', fill='x', padx=2, pady=2)
                self._list_pckr.pack(side='left', fill='x', padx=2, pady=2, expand=True)
                if self._interv:
                    self._list_pckr.set_var(self._interv)
                self._set_getter(self._list_pckr)
                self._index = 2

    def _set_getter(self, widget) -> None:
        """
        Sets the getter function based on child widget picked.
        """
        self._getter_function = widget.get_var
    
    def set_upper_limit(self, val: int) -> None:
        """
        Tells the widget how many samples there is.
        """
        self._interval_pckr._u_lim = val
        self._list_pckr._u_lim = val

    def get_value(self) -> tuple[int,list[int]]:
        """
        Returns the parameter
        """
        _output = []
        
        if self._index != 0:
            _output: list[int] = [int(i)-1 for i in self._getter_function().split(',')]
        
        return  (self._index, _output)
    

class GraphColorPicker(ctk.CTkFrame, Observer):
    """
    Picking the color of the exported graphs/plots.
    """
    def __init__(self, master, color: str) -> None:
        super().__init__(master)

        self._color: str = color

        self._toggle: ctk.CTkSwitch = ctk.CTkSwitch(self,
            text='Use preview color', width=150,
            command=lambda: self._on_check())
        self._color_pckr: ColorPicker = ColorPicker(self)
        self._color_pckr.update_clr_and_intvars(color)
        self._toggle.toggle()

        self.obs_listen(Signal.COLOR, self, self.on_preview_press)

        self._toggle.pack(side='left')

    def _on_check(self) -> None:
        """
        When the toggle is toggled.
        """
        if self._toggle.get():
            self._color_pckr.pack_forget()
            self._toggle.configure(text='Use preview color')
        else:
            self._toggle.configure(text='Pick a color')
            self._color_pckr.pack(side='top', padx=2, pady=2)

    def on_preview_press(self, color: str) -> None:
        """
        Triggered by a preview button press From the clr_pikr: ColorPicker.
        - `color`: hex color.
        """
        self._color = color

    def get_value(self) -> str:
        """
        Returns the color.
        """
        return self._color