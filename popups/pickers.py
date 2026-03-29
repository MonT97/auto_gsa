'''
Save inputs manipulation.
'''
from collections.abc import Callable

from shared_widgets import ColorPicker

import customtkinter as ctk

#TODO: find a better way to handle defaults.
class BasePicker(ctk.CTkFrame):
    '''
    The base picker class:
    - widgets:
        - check_box: ctk.CheckBox -> for en/disabling the entry field.
        - entry: ctk.Entry -> for data entry.
    - Prams:
        - label_txt: the check_box's label.
        - default_value: the default value
    '''
    def __init__(self, master, label_txt: str, default_value: str) -> None:
        super().__init__(master)
        self.val = default_value
        
        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
                    text=label_txt, checkbox_height=20, checkbox_width=20,
                    width= 150, command=lambda: self._activation())
        
        self.entry: ctk.CTkEntry = ctk.CTkEntry(self, placeholder_text=default_value)
        self.entry.configure(state=ctk.DISABLED, border_color='#565b5e')

        self.check_box.pack(side='left')
        self.entry.pack(side='left', fill='x', expand=True)
    
    def _activation(self) -> None:
        '''
        Enables/Disables the widget.
        '''
        _enabled: bool = bool(self.check_box.get())
        
        if _enabled:
            self.entry.configure(state=ctk.NORMAL, border_color='#7a848d')
            self.entry.configure(placeholder_text='')
            self.entry.focus_set()
        else:
            self.entry.configure(placeholder_text=self.val)
            self.entry.configure(state=ctk.DISABLED, border_color='#565b5e')
    
    def get_value(self) -> str:
        '''
        Returns the value.
        '''
        _value = self.entry.get()
        return _value if _value else self.val


class IntervalPicker(ctk.CTkFrame):
    '''
    Picking the interval, which files to save.
    '''
    def __init__(self, master) -> None:
        super().__init__(master)

        class IntPckr(ctk.CTkFrame):

            def __init__(self, master):
                super().__init__(master)

                _padding: float = .2
                self.configure(height=28)
                
                self.to: ctk.CTkLabel = ctk.CTkLabel(self, text='to')
                self.u_limit: ctk.CTkEntry = ctk.CTkEntry(self,
                        width=28, placeholder_text='00')
                self.l_limit: ctk.CTkEntry = ctk.CTkEntry(self,
                        width=28, placeholder_text='00')

                self.u_limit.place(anchor='w', relx=0+_padding, rely=.5)
                self.to.place(anchor='n', relx=.5, rely=.5)
                self.l_limit.place(anchor='e', relx=1-_padding, rely=.5)

            def get_var(self) -> str:

                return self.u_limit.get()+self.l_limit.get()


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
    
    def set_getter(self, widget) -> None:
        '''
        Sets the getter function based on child widget picked.
        '''
        self.getter_function = widget.get_var

    def get_value(self) -> tuple[int,list[int|None]]:
        '''
        Returns the parameter
        '''
        _output = []

        if self.index != 0:
            _output: list[int|None] = [int(i)-1 for i in self.getter_function() if i.isnumeric()]

        return  (self.index, _output)
    

class GraphColorPicker(ctk.CTkFrame):
    '''
    Picking the paths to house the results within.
    '''
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
        '''
        Triggerd by a preview button press From the clr_pikr: ColorPicker.
        '''
        self.color = color

    def get_value(self) -> str:
        '''
        Returns the color.
        '''
        return self.color