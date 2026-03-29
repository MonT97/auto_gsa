'''
Pop-up screens.
'''
import customtkinter as ctk

from .pickers import BasePicker, IntervalPicker, GraphColorPicker
from typedefs import SaveObject
from mixins import Defaults


class BaseScreen(ctk.CTkToplevel):
    '''
    The Base screen class.
    '''
    def __init__(self, master, title: str = 'Title',
                 approve_label: str = 'approve', cancel_label: str = 'close',
                 size: tuple[int,int] = (450,250)) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.geometry(f"{size[0]}x{size[1]}")

        self.bind('<Enter>', lambda _: self.focus_set())

        self.main_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.button_frame: ctk.CTkFrame = ctk.CTkFrame(self)

        self.approve_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text=approve_label, width=150)
        self.cancel_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text=cancel_label, width=150, command= lambda: self.close())

        self.cancel_btn.pack(side='left', fill='x', expand=False)
        self.approve_btn.pack(side='right', fill='x', expand=False)

        self.main_frame.pack(side='top', fill='x', padx=5, pady=5)
        self.button_frame.pack(side='bottom', fill='x', padx=5, pady=5)

        self.after(200, lambda: self.iconbitmap('assets/icon.ico'))

    def close(self) -> None:
        '''
        Closes the window.
        '''
        self.destroy()


#TODO: a way to remember what we did before, a running singlton of sorts; LTS.
class ExportScreen(BaseScreen, Defaults):
    '''
    The save all confirmation dialougue widget.
    '''
    def __init__(self, master) -> None:
        super().__init__(master, title='export', approve_label='export')
        self.master = master
        self.approve_btn.configure(command=self.on_approve)

        self.params: SaveObject = self.df_get_default(SaveObject())
        self.default_color: str = self.params.color #TODO: universaize!

        self.prfx_pckr: BasePicker = BasePicker(self.main_frame, 'Prefix', self.params.prefix)
        self.folder_name_pckr: BasePicker = BasePicker(
                    self.main_frame, 'Folder name', self.params.results_folder_name)
        self.results_path_pckr: BasePicker = BasePicker(
                    self.main_frame, 'Path', self.params.results_path)
        self.graph_clr_pckr: GraphColorPicker = GraphColorPicker(self.main_frame)
        #TODO: should know about the n of samples
        self.sample_pckr: IntervalPicker = IntervalPicker(self.main_frame) 

        self.sample_pckr.pack(expand=True, fill='x', padx=2, pady=5)
        self.prfx_pckr.pack(expand=True, fill='x', padx=2, pady=5)
        self.results_path_pckr.pack(expand=True, fill='x', padx=2, pady=5)
        self.folder_name_pckr.pack(expand=True, fill='x', padx=2, pady=5)
        self.graph_clr_pckr.pack(expand=True, fill='x', padx=2, pady=5)

    def set_color(self, color: str) -> None:
        #? Can it be standardized.
        '''
        Sets the color.
        '''
        self.graph_clr_pckr.color = color

    def on_approve(self) -> None:
        '''
        Sets the parameters.
        '''
        self.params.prefix = self.prfx_pckr.get_value()
        self.params.results_path = self.results_path_pckr.get_value()
        self.params.results_folder_name = self.folder_name_pckr.get_value()
        self.params.interval  = self.sample_pckr.get_value()
        self.params.color = self.graph_clr_pckr.color if self.graph_clr_pckr.get_value() else self.default_color
        # As the toplevel() from a ctk.TopLevel isn't the same, so, master is needed!
        self.master.winfo_toplevel().event_generate("<<Screens-save>>")
    
    def get_params(self) -> SaveObject:
        '''
        Returns the parameters.
        '''
        return self.params