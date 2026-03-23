'''
Pop-up screens.
'''
import customtkinter as ctk

from typedefs import SaveObject
from .pickers import PrefixPicker, FolderPicker


class BaseScreen(ctk.CTkToplevel):
    '''
    The Base screen class.
    '''
    def __init__(self, master, size: tuple[int,int] = (450,150)) -> None:
        super().__init__(master)
        self.resizable(False, False)
        self.geometry(f"{size[0]}x{size[1]}")

        self.params: SaveObject = SaveObject()

        self.main_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.button_frame: ctk.CTkFrame = ctk.CTkFrame(self)

        self.approve: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='ok')
        self.cancel: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='close', command= lambda: self.close())

        self.cancel.pack(side='left', fill='x', expand=True, padx=5)
        self.approve.pack(side='left', fill='x', expand=True, padx=5)

        self.main_frame.pack(side='top', fill='x', padx=5, pady=5)
        self.button_frame.pack(side='bottom', fill='x', padx=5, pady=5)

    def close(self) -> None:
        '''
        Closes the window.
        '''
        self.destroy()


class SaveAll(BaseScreen):
    '''
    The save all confirmation widget.
    '''
    def __init__(self, master) -> None:
        super().__init__(master)
        self.title('Save All')

        self.master = master
        self.approve.configure(command= self.set_params)

        self.prfx_pckr: PrefixPicker = PrefixPicker(self.main_frame)
        self.folder_name_pckr: FolderPicker = FolderPicker(self.main_frame)

        self.prfx_pckr.pack(expand=True, fill='x', padx=5, pady=5)
        self.folder_name_pckr.pack(expand=True, fill='x', padx=5, pady=5)

    def set_params(self) -> None:
        '''
        Sets the parameters.
        '''
        self.params.prefix = self.prfx_pckr.get_value()
        self.params.results_folder_name = self.folder_name_pckr.get_value()
        # As the toplevel() from a ctk.TopLevel isn't the same, master is needed!
        self.master.winfo_toplevel().event_generate("<<Screens-save>>")
    
    def get_params(self) -> SaveObject:
        '''
        Returns the parameters.
        '''
        return self.params