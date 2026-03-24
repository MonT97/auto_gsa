'''
Pop-up screens.
'''
import customtkinter as ctk

from typedefs import SaveObject
from .pickers import PrefixPicker, FolderNamePicker, ResultsPathPicker, GraphColorPicker


class BaseScreen(ctk.CTkToplevel):
    '''
    The Base screen class.
    '''
    def __init__(self, master, title: str = 'Title', size: tuple[int,int] = (450,200)) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.geometry(f"{size[0]}x{size[1]}")

        self.bind('<Enter>', lambda _: self.focus_set())

        self.main_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.button_frame: ctk.CTkFrame = ctk.CTkFrame(self)

        self.approve_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='ok', width=150)
        self.cancel_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='close', width=150, command= lambda: self.close())

        self.cancel_btn.pack(side='left', fill='x', expand=False)
        self.approve_btn.pack(side='right', fill='x', expand=False)

        self.main_frame.pack(side='top', fill='x', padx=5, pady=5)
        self.button_frame.pack(side='bottom', fill='x', padx=5, pady=5)

    def close(self) -> None:
        '''
        Closes the window.
        '''
        self.destroy()


class SaveAll(BaseScreen):
    '''
    The save all confirmation dialougue widget.
    '''
    def __init__(self, master) -> None:
        super().__init__(master, title='save all')
        self.master = master
        self.approve_btn.configure(command= self.set_params)

        self.params: SaveObject = SaveObject()
        self.params.color = '#1f7bb4'

        self.prfx_pckr: PrefixPicker = PrefixPicker(self.main_frame)
        self.folder_name_pckr: FolderNamePicker = FolderNamePicker(self.main_frame)
        self.results_path_pckr: ResultsPathPicker = ResultsPathPicker(self.main_frame)
        self.graph_clr_pckr: GraphColorPicker = GraphColorPicker(self.main_frame)

        self.graph_clr_pckr.pack(expand=True, fill='x', padx=2, pady=5)
        self.prfx_pckr.pack(expand=True, fill='x', padx=2, pady=5)
        self.results_path_pckr.pack(expand=True, fill='x', padx=2, pady=5)
        self.folder_name_pckr.pack(expand=True, fill='x', padx=2, pady=5)

    def change_default_path(self, path: str) -> None:
        '''
        Changes the default path to save into.
        '''
        self.results_path_pckr.change_default_value(path)

    def set_color(self, color: str) -> None:
        #? Can it be standardized.
        '''
        Sets the color.
        '''
        self.color = color

    def set_params(self) -> None:
        '''
        Sets the parameters.
        '''
        self.params.prefix = self.prfx_pckr.get_value()
        self.params.resutls_path = self.results_path_pckr.get_value()
        self.params.results_folder_name = self.folder_name_pckr.get_value()
        if self.graph_clr_pckr.get_value():
            self.params.color = self.color
        print(self.color)
        # As the toplevel() from a ctk.TopLevel isn't the same, so, master is needed!
        self.master.winfo_toplevel().event_generate("<<Screens-save>>")
    
    def get_params(self) -> SaveObject:
        '''
        Returns the parameters.
        '''
        return self.params