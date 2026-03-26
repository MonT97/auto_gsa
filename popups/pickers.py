'''
Save inputs manipulation.
'''
from collections.abc import Callable

import customtkinter as ctk

#TODO: find a better way to handle defaults.

class BasePicker(ctk.CTkFrame):
    '''
    The base picker class.
    '''
    def __init__(self, master, label_txt: str) -> None:
        super().__init__(master)
        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
                    text=label_txt, checkbox_height=20, checkbox_width=20,
                    width= 150, command=lambda: self._activation())
        
        self.check_box.pack(side='left')
    
    def _get_widgets(self) -> list:
        '''
        All widgets other than the checkbox.
        '''
        return self.winfo_children()[1:]

    def _pack_all(self) -> None:
        '''
        Layout the rest of the widgets.
        '''    
        for widget in self._get_widgets():
            widget.pack(side='left', fill='x', expand=True)

    def _activation(self) -> None:
        '''
        Enables/Disables the widget.
        '''
        _enabled: bool = bool(self.check_box.get())
        _state = ctk.NORMAL if _enabled else ctk.DISABLED

        for widget in self._get_widgets():
            widget.configure(state=_state)


class PrefixPicker(BasePicker):
    '''
    Picking the prefix to add to the results files names.
    '''
    def __init__(self, master) -> None:
        super().__init__(master, 'Prefix')
        self.prfx_var: ctk.StringVar = ctk.StringVar(self, value='results_')
        self.prfx_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                    state=ctk.DISABLED, textvariable=self.prfx_var)
        
        self._pack_all()
    
    def get_value(self) -> str:
        '''
        Returns the parameters.
        '''
        return self.prfx_var.get()


class FolderNamePicker(BasePicker):
    '''
    Picking the Folder to house the results within.
    '''
    def __init__(self, master) -> None:
        super().__init__(master, 'Folder Name')
        self.folder_name_var: ctk.StringVar = ctk.StringVar(self, value='analysis_results')
        self.entry: ctk.CTkEntry = ctk.CTkEntry(self,
                    state=ctk.DISABLED, textvariable=self.folder_name_var)
        
        self._pack_all()
    
    def get_value(self) -> str:
        '''
        Returns the parameters.
        '''
        return self.folder_name_var.get()


class ResultsPathPicker(BasePicker):
    '''
    Picking the paths to house the results within.
    '''
    def __init__(self, master) -> None:
        super().__init__(master, 'Path')
        self.dir_var: ctk.StringVar = ctk.StringVar(self, value='results\\files\\path')
        self.entry: ctk.CTkEntry = ctk.CTkEntry(self,
                    state=ctk.DISABLED, textvariable=self.dir_var)
        
        self._pack_all()
    
    def change_default_value(self, value: str) -> None:
        '''
        Changes the default value of the parameter.
        '''
        self.dir_var.set(value)

    def get_value(self) -> str:
        '''
        Returns the parameters.
        '''
        return self.dir_var.get()


class IntervalPicker(ctk.CTkFrame):
    '''
    Picking the interval, which files to save.
    '''
    def __init__(self, master) -> None:
        super().__init__(master)

        class IntPckr(ctk.CTkFrame):

            def __init__(self, master):
                super().__init__(master)

                self.u_var: ctk.StringVar = ctk.StringVar(self, value='0')
                self.l_var: ctk.StringVar = ctk.StringVar(self, value='0')

                self.to: ctk.CTkLabel = ctk.CTkLabel(self, text='to')
                self.u_limit: ctk.CTkEntry = ctk.CTkEntry(self,
                    textvariable=self.u_var, width=25)
                self.l_limit: ctk.CTkEntry = ctk.CTkEntry(self,
                    textvariable=self.l_var, width=25)

                self.u_limit.pack(side='left', padx=4)
                self.to.pack(side='left')
                self.l_limit.pack(side='left', padx=4)
            
            def get_var(self) -> str:

                return self.u_var.get()+self.l_var.get()


        class ListPckr(ctk.CTkFrame):

            def __init__(self, master) -> None:
                super().__init__(master)

                self.list_var: ctk.StringVar = ctk.StringVar(self, value='1, 2, 3,...')
                self.list_entry: ctk.CTkEntry = ctk.CTkEntry(self,
                            textvariable=self.list_var)

                self.list_entry.pack()
            
            def get_var(self) -> str:

                return self.list_var.get()

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
                self.interval_pckr.pack(side='top')
                self.set_getter(self.interval_pckr)
                self.index = 1
            case 'list':
                self.drop_down.pack(side='left', fill='x')
                self.list_pckr.pack(side='left', expand=True, fill='x')
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
        _output: list[int|None] = [int(i)-1 for i in self.getter_function() if i.isnumeric()]
        if self.index == 0:
            _output = []
        return  (self.index, _output)
    

class GraphColorPicker(ctk.CTkFrame):
    '''
    Picking the paths to house the results within.
    '''
    def __init__(self, master) -> None:
        super().__init__(master)

        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
            text='Use color from preview',
            checkbox_height=20, checkbox_width=20)

        self.check_box.pack(side='left')

    def get_value(self) -> bool:
        
        return bool(self.check_box.get())