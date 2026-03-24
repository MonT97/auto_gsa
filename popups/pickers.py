'''
Save inputs manipulation.
'''
import customtkinter as ctk

class BasePicker(ctk.CTkFrame):
    def __init__(self, master, label_txt: str) -> None:
        super().__init__(master)
        '''
        The base picker class.
        '''
        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
                    text=label_txt, checkbox_height=20, checkbox_width=20,
                    command=lambda: self._activation())
        
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


class GraphColorPicker(ctk.CTkFrame):
    '''
    Picking the paths to house the results within.
    '''
    def __init__(self, master) -> None:
        super().__init__(master)

        self.check_box: ctk.CTkCheckBox = ctk.CTkCheckBox(self,
            text='Use color from preview', checkbox_height=20, checkbox_width=20)

        self.check_box.pack(side='left')
    

    def get_value(self) -> bool:
        
        return bool(self.check_box.get())
