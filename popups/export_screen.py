import os

import customtkinter as ctk

from mixins import Defaults, HasToolTip
from typedefs import SaveObject
from utils import utls

from .base_screen import BaseScreen
from .pickers import (BasePicker, BaseToggle, DpiPicker, GraphColorPicker, IntervalPicker)

# Constant
# fonts:
BTN_FRAME_FONT = ('Arial', 16)

#TODO: a way to remember what we did before, a running singlton of sorts; LTS.
class ExportScreen(BaseScreen, Defaults, HasToolTip):
    """
    The export confirmation dialougue screen.
    """
    def __init__(self, master, use_global_defaults: bool = False) -> None:
        """
        The export confirmation dialougue screen.
        - use_global_defaults: If true, the [ExportScreen] uses the global default values instead of the latest used.
        """
        super().__init__(master, title='export screen', approve_label='export')

        self.master = master
        self.use_global_defaults: bool = use_global_defaults
        self.approve_btn.configure(command=self._on_approve)

        #This is a hard coded value; trail&error driven.
        _x_offset: int = 500
        self.pos: tuple[int,int] = (
            (self.master.winfo_screenwidth()+_x_offset)//4,
            self.master.winfo_screenheight()//4)
        
        self.geometry(f'{self.size[0]}x{self.size[1]+20}+{self.pos[0]}+{self.pos[1]}')

        self.save_params: SaveObject = self.df_get(SaveObject) if not use_global_defaults else self.df_get_from_file(SaveObject)
        self.default_color: str = self.save_params.color

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='show folder', width=150, state=ctk.DISABLED,
                    command=lambda: self.on_show_btn())

        self.quli_frame = ctk.CTkFrame(self.main_frame)

        # Pickers:
        self.prfx_pckr = BasePicker(self.main_frame, 'Prefix', self.save_params.prefix)
        self.folder_name_pckr = BasePicker(self.main_frame,
                'Folder name', self.save_params.results_folder_name)
        self.results_path_pckr = BasePicker(self.main_frame,
                'Path', self.save_params.results_path)
        self.dpi_picker = DpiPicker(self.main_frame,
                'Dpi', str(self.save_params.dpi),
                'The resolution of the graphs, higher is better')
        self.graph_clr_pckr = GraphColorPicker(self.main_frame)  
        self.sample_pckr = IntervalPicker(self.main_frame)

        self.raws_pckr = BaseToggle(self.quli_frame,
                'Save raw files?',
                'Export raw/un-interpreted spreadsheets.')
        self.trans_pckr = BaseToggle(self.quli_frame,
                'Transparent',
                'Transparent graphs.')

        self.btn_frame_font = ctk.CTkFont(*BTN_FRAME_FONT)
        self.cancel_btn.configure(font=self.btn_frame_font)
        self.approve_btn.configure(font=self.btn_frame_font)

        # Layout:
        self.trans_pckr.pack(side='right', expand=True, fill='x', padx=2, pady=2)
        self.raws_pckr.pack(side='right', expand=True, fill='x', padx=2, pady=2)

        self.sample_pckr.pack(fill='x', padx=2, pady=(2,2))
        self.quli_frame.pack(fill='x', padx=2, pady=(2,0))
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
        self.graph_clr_pckr.color = color

    def _on_approve(self) -> None:
        """
        Sets the SaveObj.
        """
        self.save_params.prefix = self.prfx_pckr.get_value()
        self.save_params.results_path = self.results_path_pckr.get_value()
        self.save_params.results_folder_name = self.folder_name_pckr.get_value()
        self.save_params.interval  = self.sample_pckr.get_value()
        self.save_params.color = self.graph_clr_pckr.color if self.graph_clr_pckr.get_value() else self.default_color
        self.save_params.dpi = int(self.dpi_picker.get_value())
        self.save_params.save_raw_files = self.raws_pckr.get_value()
        self.save_params.transparent = self.trans_pckr.get_value()
        
        # As the toplevel() from a ctk.TopLevel isn't the same, so, master is needed!
        self.master.winfo_toplevel().event_generate("<<Screens-saved>>")

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
        return self.save_params