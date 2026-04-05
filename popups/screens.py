"""
Pop-up screens.
"""
from PIL import Image

from .pickers import BasePicker, IntervalPicker, GraphColorPicker, SaveRawsPicker
from mixins import Defaults, HasToolTip
from typedefs import SaveObject

import os
import customtkinter as ctk

class BaseScreen(ctk.CTkToplevel, HasToolTip):
    """
    The Base screen class.
    """
    def __init__(self, master, title: str = 'Title',
                 approve_label: str = 'approve', cancel_label: str = 'close',
                 size: tuple[int,int] = (450,300)) -> None:
        super().__init__(master)
        self.size = size
        self.title(title)
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.geometry(f"{self.size[0]}x{self.size[1]}")

        self.bind('<Enter>', lambda _: self.focus_set())

        self.main_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.button_frame: ctk.CTkFrame = ctk.CTkFrame(self, height=30)

        self.export_btn_icon: ctk.CTkImage = ctk.CTkImage(
            Image.open('assets/upload.png'), size=(11,11))
        self.approve_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text=approve_label, width=150, image=self.export_btn_icon)
        self.htt_tip(self.approve_btn, 'export.')

        self.cancel_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text=cancel_label, width=150, command= lambda: self.close())

        self.cancel_btn.place(anchor='w', relx=0, rely=.5, relwidth=.2, relheight=1)
        self.approve_btn.place(anchor='e', relx=1, rely=.5, relwidth=.2, relheight=1)

        self.main_frame.pack(side='top', fill='x', padx=5, pady=5)
        self.button_frame.pack(side='bottom', fill='x', padx=5, pady=5)

        self.after(200, lambda: self.iconbitmap('assets/default.ico'))

    def close(self) -> None:
        """
        Closes the window.
        """
        self.destroy()


#TODO: a way to remember what we did before, a running singlton of sorts; LTS.
class ExportScreen(BaseScreen, Defaults, HasToolTip):
    """
    The export confirmation dialougue widget.
    """
    def __init__(self, master, use_global_defaults: bool = False) -> None:
        super().__init__(master, title='export', approve_label='')
        self.master = master
        self.use_global_defaults: bool = use_global_defaults
        self.approve_btn.configure(command=self.on_approve)

        #This is a hard coded value; trail&error driven.
        self.pos: tuple[int,int] = (
            (self.master.winfo_screenwidth()+500)//4,
            self.winfo_screenheight()//4)
        
        self.geometry(f'{self.size[0]}x{self.size[1]}+{self.pos[0]}+{self.pos[1]}')

        self.params: SaveObject = self.df_get(SaveObject) if not use_global_defaults else self.df_get_from_file(SaveObject)
    
        self.default_color: str = self.params.color #TODO: universaize!

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='show folder', width=150, state=ctk.DISABLED,
                    command=lambda: self.on_show_btn())

        self.prfx_pckr: BasePicker = BasePicker(self.main_frame, 'Prefix', self.params.prefix)
        self.folder_name_pckr: BasePicker = BasePicker(
                    self.main_frame, 'Folder name', self.params.results_folder_name)
        self.results_path_pckr: BasePicker = BasePicker(
                    self.main_frame, 'Path', self.params.results_path)
        self.graph_clr_pckr: GraphColorPicker = GraphColorPicker(self.main_frame)  
        self.sample_pckr: IntervalPicker = IntervalPicker(self.main_frame)
        self.raws_pckr: SaveRawsPicker = SaveRawsPicker(self.main_frame,
                    'Export raw/un-interpreted spreadsheets.')

        self.sample_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.raws_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.prfx_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.results_path_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.folder_name_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.graph_clr_pckr.pack(expand=True, fill='x', padx=2, pady=2)

    def set_limit(self, val: int) -> None:
        """
        Sets the interval cap, which is the number of active samples.
        """
        self.sample_pckr.set_upper_limit(val)

    def set_color(self, color: str) -> None:
        """
        Sets the color.
        """
        self.graph_clr_pckr.color = color

    def on_approve(self) -> None:
        """
        Sets the SaveObj.
        """
        self.params.prefix = self.prfx_pckr.get_value()
        self.params.results_path = self.results_path_pckr.get_value()
        self.params.results_folder_name = self.folder_name_pckr.get_value()
        self.params.interval  = self.sample_pckr.get_value()
        self.params.color = self.graph_clr_pckr.color if self.graph_clr_pckr.get_value() else self.default_color
        self.params.raw_files = self.raws_pckr.get_value()
        # As the toplevel() from a ctk.TopLevel isn't the same, so, master is needed!
        self.master.winfo_toplevel().event_generate("<<Screens-saved>>")

    def set_results_path(self, path: str) -> None:
        """
        Outside trigger, when export is complete.
        - path[str]: the reults folder path. 
        """
        self.results_path: str = path
        self.show_btn.configure(state=ctk.NORMAL)
        self.show_btn.place(anchor='n', relx=.5, rely=0, relwidth=.20, relheight=1)
        self.htt_tip(self.show_btn, 'open the results folder')

    def on_show_btn(self) -> None:
        """
        Opens the latest results folder in the file manager.
        """
        os.startfile(self.results_path)

    def get_params(self) -> SaveObject:
        """
        Returns the SaveObj.
        """
        return self.params