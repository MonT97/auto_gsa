import os
from typing import Callable

import customtkinter as ctk

from mixins import Defaults, HasToolTip, Observer
from typedefs import SaveObject
from utils import utls

from .base_screen import BaseScreen
from .pickers import (BasePicker, BaseToggle, DpiPicker, GraphColorPicker,
                      IntervalPicker)

# Constant

# screen:
X_OFFSET = 500
SCREEN_SIZE = (450,315)

# fonts:
BTN_FRAME_FONT = ('Arial', 16)

#TODO: a way to remember what we did before, a running singlton of sorts; LTS.
class ExportScreen(BaseScreen, Defaults, HasToolTip, Observer):
    """
    The export confirmation dialougue screen.
    """
    def __init__(self, master,
                connection_func: Callable, use_global_defaults: bool = False) -> None:
        """
        The export confirmation dialougue screen.
        - use_global_defaults: If true, the [ExportScreen] uses the global default values instead of the latest used.
        """
        super().__init__(master, title='export screen', approve_label='export', size=SCREEN_SIZE)

        self.master = master
        self.use_global_defaults: bool = use_global_defaults
        self.approve_btn.configure(command=lambda: self._on_approve(connection_func))

        #defaults:
        self.default_path: str = ''

        #This is a hard coded value; trail&error driven.
        self.pos: tuple[int,int] = (
            (self.master.winfo_screenwidth()+X_OFFSET)//4,
            self.master.winfo_screenheight()//4)
        
        self.geometry(f'{self.size[0]}x{self.size[1]+20}+{self.pos[0]}+{self.pos[1]}')

        self.save_obj: SaveObject = self.df_get(SaveObject) if not use_global_defaults else self.df_get_from_file(SaveObject)
        self.default_color: str = self.save_obj.color

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='show folder', width=150, state=ctk.DISABLED,
                    command=lambda: self.on_show_btn())

        self.qualifiers_frame = ctk.CTkFrame(self.main_frame)

        # Pickers:
        self.prfx_pckr = BasePicker(self.main_frame, 'Prefix', self.save_obj.prefix)
        self.folder_name_pckr = BasePicker(self.main_frame,
                'Folder name', self.save_obj.results_folder_name)
        self.results_path_pckr = BasePicker(self.main_frame,
                'Path', self.save_obj.results_path)
        
        self.dpi_picker = DpiPicker(self.main_frame,
                'Dpi', str(self.save_obj.dpi),
                'The resolution of the graphs, higher is better')
        self.graph_clr_pckr = GraphColorPicker(self.main_frame)  
        self.sample_pckr = IntervalPicker(self.main_frame)

        self.raws_pckr = BaseToggle(self.qualifiers_frame,
                'Save raw files?',
                'Export raw/un-interpreted spreadsheets.')
        self.trans_pckr = BaseToggle(self.qualifiers_frame,
                'Transparent',
                'Make graph transparent.')

        self.btn_frame_font = ctk.CTkFont(*BTN_FRAME_FONT)
        self.cancel_btn.configure(font=self.btn_frame_font)
        self.approve_btn.configure(font=self.btn_frame_font)

        # Layout:
        # qualifiers_frame:
        self.raws_pckr.pack(side='left', expand=True, fill='x', padx=2, pady=2)
        self.trans_pckr.pack(side='left', expand=True, fill='x', padx=2, pady=2)

        # main_frame:
        self.sample_pckr.pack(fill='x', padx=2, pady=(2,2))
        self.qualifiers_frame.pack(fill='x', padx=2, pady=(2,0))
        self.prfx_pckr.pack(fill='x', padx=2, pady=(2,0))
        self.results_path_pckr.pack(fill='x', padx=2, pady=(2,0))
        self.folder_name_pckr.pack(fill='x', padx=2, pady=(2,0))
        self.dpi_picker.pack(fill='x', padx=2, pady=(2,0))
        self.graph_clr_pckr.pack(fill='x', padx=2, pady=(2,2))

    def set_limit(self, val: int) -> None:
        """
        Sets the interval cap, which is the number of active samples.
        """
        self.sample_pckr.set_upper_limit(val)

    def set_color(self, color: str) -> None:
        """
        Sets the grphs color.
        """
        self.graph_clr_pckr.update(color)

    def set_path(self, path: str) -> None:
        """
        Sets the path.
        """
        self.results_path_pckr.update_default(path)

    def _on_approve(self, func: Callable[[SaveObject], None]) -> None:
        """
        Sets the SaveObj, triggered by approve button press.\n
        It also calls the [connection_func]/[func] delgated to the screen.
        """
        self.save_obj.prefix = self.prfx_pckr.get_value()
        self.save_obj.results_path = self.results_path_pckr.get_value() 
        self.save_obj.results_folder_name = self.folder_name_pckr.get_value()
        self.save_obj.interval  = self.sample_pckr.get_value()
        self.save_obj.color = self.graph_clr_pckr.color if self.graph_clr_pckr.get_value() else self.default_color
        self.save_obj.dpi = int(self.dpi_picker.get_value())
        self.save_obj.save_raw_files = self.raws_pckr.get_value()
        self.save_obj.transparent = self.trans_pckr.get_value()
        
        func(self.save_obj)

    def set_results_path(self, path: str) -> None:
        """
        Outside signal triggered, when export is complete.
        - path[str]: the results folder path. 
        """
        self.results_path: str = path
        self.show_btn.configure(state=ctk.NORMAL)
        self.show_btn.place(anchor='n', relx=.5, rely=0, relwidth=.20, relheight=1)
        self.htt_tip(self.show_btn, 'open the results folder')

    def on_show_btn(self) -> None:
        """
        Opens the latest results folder in the file explorer.
        """
        os.startfile(self.results_path)

    def get_params(self) -> SaveObject:
        """
        Returns the SaveObj.
        """
        return self.save_obj