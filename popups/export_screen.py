import os
from typing import Callable, Final

import customtkinter as ctk

from mixins import Defaults, HasToolTip, Observer
from models import Cache
from typedefs import SaveObject, Signal

from .base_picker import BasePicker, BaseToggle
from .base_screen import BaseScreen
from .pickers import DirPicker, DpiPicker, GraphColorPicker, IntervalPicker

# Constants
# screen:
X_OFFSET: Final[int] = 500
SCREEN_SIZE: Final[tuple[int,int]] = (450,315)

# fonts:
BTN_FRAME_FONT: Final[tuple[str,int]] = ('Arial', 16)

# cache:
KEY: Final[str] = 'final'

_saveobj_cache = Cache(1) # one element cache for one step go back


#TODO: a way to remember what we did before, a running singleton of sorts; LTS, Currently the SaveObj does this mission, should it?!.
class ExportScreen(BaseScreen, Defaults, HasToolTip, Observer):
    """
    The export confirmation dialogue screen.
    - function:
    - `use_global_defaults`: If true, the [ExportScreen] uses the global default values instead of the latest used.
    """
    def __init__(self, master, state_func: Callable, connection_func: Callable,
                 save_obj: SaveObject, use_global_defaults: bool = False) -> None:
        """
        The export confirmation dialogue screen.
        - use_global_defaults: If true, the [ExportScreen] uses the global default values instead of the latest used.
        """
        super().__init__(master, title='export screen', approve_label='export', size=SCREEN_SIZE)
        self._master = master
        self._state_func = state_func
        self._state_func(False)
        self._use_blob_def: bool = use_global_defaults

        self.approve_btn.configure(command=lambda: self._on_approve(connection_func))
        self.wm_protocol("WM_DELETE_WINDOW", lambda: self._on_close())
        self.cancel_btn.configure(command=lambda: self._on_close())
        
        #This is a hard coded value; trail&error driven.
        self._pos: tuple[int,int] = (
            (self._master.winfo_screenwidth()+X_OFFSET)//4,
            self._master.winfo_screenheight()//4)
        
        self.geometry(f'{self.size[0]}x{self.size[1]+20}+{self._pos[0]}+{self._pos[1]}')
        
        # Pick SaveObj:
        if self._use_blob_def:
            self._save_obj = self.df_get_from_file(SaveObject)
        else:
            if _saveobj_cache.check(KEY):
                _saveobj_cache.remove(KEY)
            _saveobj_cache.add(KEY, save_obj)
            self._save_obj = save_obj

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='show folder', width=150, state=ctk.DISABLED,
                    command=lambda: self._on_show_btn_pressed())

        self._qualifiers_frame = ctk.CTkFrame(self.main_frame)

        # Pickers:
        self._inter_pckr = IntervalPicker(self.main_frame, self._save_obj.get('interval'))
        self._prfx_pckr = BasePicker(self.main_frame,
                'Prefix', self._save_obj.get('prefix'),
                'A prefix to add to the resulting files, [prefix_example_name]')
        self._dpi_picker = DpiPicker(self.main_frame, 'Dpi',
                str(self._save_obj.get('dpi')), 'The resolution of the graphs, higher is better')
        self._dir_picker = DirPicker(self.main_frame, 'Export to',
                self._save_obj.get_results_path(), 'Enable to pick a folder to export into')
        self._graph_clr_pckr = GraphColorPicker(self.main_frame, self._save_obj.get('color'))  
        
        self._raws_pckr = BaseToggle(self._qualifiers_frame,
                'Save raw files?', 
                self._save_obj.get('save_raw_files'),
                'Export raw/un-interpreted spreadsheets.')
        self._trans_pckr = BaseToggle(self._qualifiers_frame,
                'Transparent', 
                self._save_obj.get('transparent'),
                'Make graph transparent.')

        self._btn_frame_font = ctk.CTkFont(*BTN_FRAME_FONT)
        self.cancel_btn.configure(font=self._btn_frame_font)
        self.approve_btn.configure(font=self._btn_frame_font)

        # Layout:
        # qualifiers_frame:
        self._raws_pckr.pack(side='left', expand=True, fill='x', padx=2, pady=2)
        self._trans_pckr.pack(side='left', expand=True, fill='x', padx=2, pady=2)

        # main_frame:
        self._inter_pckr.pack(fill='x', padx=2, pady=(2,2))
        self._qualifiers_frame.pack(fill='x', padx=2, pady=(2,0))
        self._prfx_pckr.pack(fill='x', padx=2, pady=(2,0))
        self._dpi_picker.pack(fill='x', padx=2, pady=(2,0))
        self._dir_picker.pack(fill='x', padx=2, pady=(2,0))
        self._graph_clr_pckr.pack(fill='x', padx=2, pady=(2,2))

    def set_limit(self, val: int) -> None:
        """
        Sets the interval cap, which is the number of active samples.
        """
        self._inter_pckr.set_upper_limit(val)

    def _update_save_obj(self) -> None:
        """
        Updates the save object.
        """
        self._save_obj.update(
            prefix = self._prfx_pckr.get_value(),
            results_path = self._dir_picker.get_path(),
            results_dir_name = self._dir_picker.get_dir_name(),
            interval  = self._inter_pckr.get_value(),
            color = self._graph_clr_pckr.get_value(),
            dpi = int(self._dpi_picker.get_value()),
            save_raw_files = self._raws_pckr.get_value(),
            transparent = self._trans_pckr.get_value())

    def _on_approve(self, func: Callable[[SaveObject], None]) -> None:
        """
        Sets the SaveObj, triggered by approve button press.\n
        It also calls the [connection_func]/[func] delegated to the screen.
        """
        self._update_save_obj()
        
        func(self._save_obj)

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
        os.startfile(self._save_obj.get_results_path())

    def get_params(self) -> SaveObject:
        """
        Returns the SaveObj.
        """
        return self._save_obj        
    
    def _on_close(self) -> None:
        """
        Triggered when closing the screen.
        """
        if not self._use_blob_def:
            if _saveobj_cache.check(KEY):
                _saveobj_cache.remove(KEY)
            self._update_save_obj()
            _saveobj_cache.add(KEY, self._save_obj)
        else:
            _clr: str = _saveobj_cache.get(KEY).get('color')
            self.obs_broadcast(Signal.COLOR, self, (_clr,))
        
        self._state_func(True)

        super().close()
