import os
from typing import Callable, Final

import customtkinter as ctk

from mixins import Defaults, HasToolTip, Observer
from typedefs import SaveObject

from .base_picker import BasePicker, BaseToggle
from .base_screen import BaseScreen
from .pickers import DirPicker, DpiPicker, GraphColorPicker, IntervalPicker

# Constants
# screen:
X_OFFSET: Final[int] = 500
SCREEN_SIZE: Final[tuple[int,int]] = (450,315)

# fonts:
BTN_FRAME_FONT: Final[tuple[str,int]] = ('Arial', 16)


#TODO: a way to remember what we did before, a running singleton of sorts; LTS, Currently the SaveObj does this mission.
class ExportScreen(BaseScreen, Defaults, HasToolTip, Observer):
    """
    The export confirmation dialogue screen.
    """
    def __init__(self, master, connection_func: Callable,
                 save_obj: SaveObject, use_global_defaults: bool = False) -> None:
        """
        The export confirmation dialogue screen.
        - use_global_defaults: If true, the [ExportScreen] uses the global default values instead of the latest used.
        """
        super().__init__(master, title='export screen', approve_label='export', size=SCREEN_SIZE)

        self.master = master
        self.use_global_defaults: bool = use_global_defaults
        self.approve_btn.configure(command=lambda: self._on_approve(connection_func))
        
        self.save_obj = save_obj if not use_global_defaults else self.df_get_from_file(SaveObject)
        
        #This is a hard coded value; trail&error driven.
        self.pos: tuple[int,int] = (
            (self.master.winfo_screenwidth()+X_OFFSET)//4,
            self.master.winfo_screenheight()//4)
        
        self.geometry(f'{self.size[0]}x{self.size[1]+20}+{self.pos[0]}+{self.pos[1]}')

        self.default_color: str = self.save_obj.color

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='show folder', width=150, state=ctk.DISABLED,
                    command=lambda: self._on_show_btn_pressed())

        self.qualifiers_frame = ctk.CTkFrame(self.main_frame)

        # Pickers:
        self.prfx_pckr = BasePicker(self.main_frame,
                'Prefix', self.save_obj.prefix,
                'A prefix to add to the resulting files, [prefix_example_name]')
        self.dir_picker = DirPicker(self.main_frame, 'Folder picker',
                self.save_obj.get_results_path(), 'Enable to pick a folder to export into')
        self.dpi_picker = DpiPicker(self.main_frame, 'Dpi',
                str(self.save_obj.dpi), 'The resolution of the graphs, higher is better')
        self.graph_clr_pckr = GraphColorPicker(self.main_frame, self.save_obj.color)  
        self.inter_pckr = IntervalPicker(self.main_frame)

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
        self.inter_pckr.pack(fill='x', padx=2, pady=(2,2))
        self.qualifiers_frame.pack(fill='x', padx=2, pady=(2,0))
        self.dir_picker.pack(fill='x', padx=2, pady=(2,0))
        self.prfx_pckr.pack(fill='x', padx=2, pady=(2,0))
        self.dpi_picker.pack(fill='x', padx=2, pady=(2,0))
        self.graph_clr_pckr.pack(fill='x', padx=2, pady=(2,2))

    def set_limit(self, val: int) -> None:
        """
        Sets the interval cap, which is the number of active samples.
        """
        self.inter_pckr.set_upper_limit(val)

    def _on_approve(self, func: Callable[[SaveObject], None]) -> None:
        """
        Sets the SaveObj, triggered by approve button press.\n
        It also calls the [connection_func]/[func] delegated to the screen.
        """
        self.save_obj.prefix = self.prfx_pckr.get_value()
        self.save_obj.results_path = self.dir_picker.get_path()
        self.save_obj.results_dir_name = self.dir_picker.get_dir_name()
        self.save_obj.interval  = self.inter_pckr.get_value()
        self.save_obj.color = self.graph_clr_pckr.color if self.graph_clr_pckr.get_value() else self.default_color
        self.save_obj.dpi = int(self.dpi_picker.get_value())
        self.save_obj.save_raw_files = self.raws_pckr.get_value()
        self.save_obj.transparent = self.trans_pckr.get_value()
        
        func(self.save_obj)

    def on_exported(self) -> None:
        """
        Enables [self.show_btn], signal triggered.
        """
        self.show_btn.configure(state=ctk.NORMAL)
        self.show_btn.place(anchor='n', relx=.5, rely=0, relwidth=.20, relheight=1)
        self.htt_tip(self.show_btn, 'open the results folder in the file explorer')

    def _on_show_btn_pressed(self) -> None:
        """
        Opens the latest results folder in the file explorer.
        """     
        os.startfile(self.save_obj.get_results_path())

    def get_params(self) -> SaveObject:
        """
        Returns the SaveObj.
        """
        return self.save_obj