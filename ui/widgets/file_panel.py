import os
import time
import numpy as np
import tkinter as tk
from tkinter import ttk
from typing import Callable, Final

import customtkinter as ctk
from PIL import Image

from mixins import CanSave, Defaults, HasToolTip, Observer, Validator
from models import Cache, Sample
from popups import ExportScreen, ImportScreen
from typedefs import GraphType, LogMsgType, SaveObject, Signal
from utils import utls

# Constants:
# colors
DEFAULT_GRAPH_COLOR: Final[str] = '#1f7bb4'
ACTIVE_ENTRY: Final[str] = '#ffffff' #! Base entry class?!
DEFAULT_ENTRY: Final[str] = '#565b5e'

# fonts
ENTRY_FONT: Final[tuple[str, int]] = ('Arial', 16)

# icons
ICON_SIZE: Final[tuple[int,int]] = (15,15)
IMPORT_ICON: Final = Image.open('assets/import.png')
EXPORT_ICON: Final = Image.open('assets/upload.png')
EXPORT_DIS_ICON: Final = Image.open('assets/upload_dis.png')

# shortcuts
IMPORT: Final[str] = 'i'
EXPORT: Final[str] = 'e'
ANALYZE: Final[str] = 'a'

# convention to keep:
# file -> file_name.extension
# sample -> Sample(file_path)

class FilePanel(ctk.CTkFrame, CanSave, Defaults, HasToolTip, Observer):
    """
    CTkFrame:
    The class handling:
        - Entering the samples path [entry].
        - Picking a sample [file_viewer].
        - Analyzing the sample [analyze_btn].
        - Saving the results [save_btn]/[export_btn].
    """
    def __init__(self, master):
        super().__init__(master)
        #!config = add to a permanent config file!.
        self.configure(corner_radius=0)

        self._master = master
        self.__root = utls.get_root(self)
        self._crnt_sample: Sample = Sample()

        # Caching:
        self._path_cache: list[str] = []
        self._samples_cache: Cache = Cache(50)

        # pass around data holder.
        self._save_obj: SaveObject = self.df_get(SaveObject)

        #type due to the strange return of the treeview selection method
        self._data: tuple[str,...] = ('',)
        self._valid_files: list[str] = []
        self._number_of_valid_files: int = 0

        # global keyboard shortcuts:
        self.__root.bind(f"<Control-KeyPress-{IMPORT}>",
                         lambda _: self._screen_import())
        self.__root.bind(f"<Control-KeyPress-{EXPORT}>",
                         lambda _: self._on_export_btn_pressed())

        # Entry related
        self._entry_font = ctk.CTkFont(*ENTRY_FONT)
        self._import_icon: ctk.CTkImage = ctk.CTkImage(IMPORT_ICON, size=ICON_SIZE)

        self._entry_frame: ctk.CTkFrame = ctk.CTkFrame(self, height=30)
        self._entry = ctk.CTkEntry(self._entry_frame,
            border_color=DEFAULT_ENTRY,
            placeholder_text="sample files folder path...")
        
        self._entry.bind("<KeyPress-Return>", lambda _: self._direct_import(self._entry.get()))
        self._entry.bind("<Enter>", lambda _: self._on_entry_active())
        self._entry.bind("<KeyPress-Up>", lambda _: self._get_from_path_cache())
        self._entry.bind("<KeyPress-Escape>", lambda _: self._reset_focus())

        self.htt_tip(self._entry, 'path to import from\n[Enter/Return]: quick import.\n[Up]: cycle back to previous entries.')
        utls.bg_transparent(self._entry)

        self._file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import",
            image=self._import_icon,
            compound='right',
            font=self._entry_font,
            command=lambda: self._screen_import())
        self.htt_tip(self._file_import_btn, 'open import screen')

        # Viewer:
        self._viewer_frame = ctk.CTkFrame(self) # <--- Necessary for ttip signal handling!
        self._file_viewer: FileViewer = FileViewer(self._viewer_frame)
        self._file_viewer.bind("<<TreeviewSelect>>", lambda _: self._set_data())
        self._file_viewer.bind("<KeyPress-Return>", lambda _: self._analyze(self._data))
        self._file_viewer.bind(f"<Control-KeyPress-{ANALYZE}>", lambda _: self._analyze(self._data))
        self._file_viewer.bind("<Leave>", lambda _: self._reset_focus())
        
        # Lower buttons:
        self._analyze_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analyze",
            font=self._entry_font,
            state=ctk.DISABLED,
            command=lambda: self._analyze(self._data))
        self.htt_tip(self._analyze_btn, 'Analyze and preview the sample file selected above')
        
        self._save_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="save",
            font=self._entry_font,
            state=ctk.DISABLED,
            command=lambda: self._on_save_btn_pressed())
        self.htt_tip(self._save_btn, 'save the analysis results of the currently selected sample')

        self._export_btn_icon: ctk.CTkImage = ctk.CTkImage(
            EXPORT_ICON, size=ICON_SIZE)
        self._export_btn_dis_icon: ctk.CTkImage = ctk.CTkImage(
            EXPORT_DIS_ICON, size=ICON_SIZE)
        self._export_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="export",
            image=self._export_btn_dis_icon,
            compound='right',
            font=self._entry_font,
            state=ctk.DISABLED, 
            command=lambda: self._on_export_btn_pressed())
        self._export_btn.bind('<Control-Button-1>',
                              lambda _: self._on_export_btn_pressed(True))
        self.htt_tip(self._export_btn, 'open export screen')        

        # layout:
        self._entry.pack(side='top', fill='x')
        self._entry_frame.pack(side="top", fill="x", padx=5, pady=(5,0))

        self._file_viewer.pack(side="top", expand=1, fill="both")

        self._file_import_btn.pack(side="top", fill="x", padx=5, pady=(5,5))
        self._viewer_frame.pack(side="top", expand=1, fill="both", padx=5, pady=(5,5))
        self._export_btn.pack(side="bottom", fill="x", padx=5, pady=(5,5))
        self._save_btn.pack(side="bottom", fill="x", padx=5, pady=(5,0))
        self._analyze_btn.pack(side="bottom", fill="x", padx=5, pady=(5,0))

    def _reset_focus(self) -> None:
        """
        Resets the focus to master from [self._entry].
        """
        self._entry.configure(border_color=DEFAULT_ENTRY)
        self._master.focus_set()

    def _on_entry_active(self) -> None:
        """
        Behavior when hovering over [self._entry].
        """
        self._entry.focus_set()
        self._entry.configure(border_color=ACTIVE_ENTRY)
        self._entry.select_range('0', ctk.END)
        self._entry.xview_scroll(len(self._save_obj.get('files_path')),'units')

    def _add_to_path_cache(self, new_path: str) -> None:
        """
        Cache [new_path] if it is not.
        """
        _crnt_path: str = self._save_obj.get('files_path')
        if (_crnt_path != new_path) and(new_path not in self._path_cache):
            self._path_cache.append(_crnt_path)

    def _get_from_path_cache(self) -> None:
        """
        Get the path from the cache if it exists.
        """
        self._path_cache.insert(0,self._save_obj.get('files_path'))
        self._save_obj.update(files_path=self._path_cache.pop())

        self._update_entry(self._save_obj.get('files_path'))

    def _update_entry(self, path: str) -> None:
        """
        Updates the [self._entry] text and scrolls to the rightmost limit.
        - call when [files_path] is updated.
        """
        self._entry.delete(0, ctk.END)
        self._entry.insert(0, path)
        self._entry.xview_scroll(len(path),'units')

    def _direct_import(self, path: str) -> None:
        """
        From [self._entry].
        """
        if not os.path.exists(path):
            self.obs_broadcast(Signal.LOG, self,
                    (f'path [{path}] is invalid or doesn\'t exist.', LogMsgType.ERROR))
            return
        
        self.set_valid_files(path)
    
    def _screen_import(self) -> None:
        """
        From the import pop-up screen.
        """
        ImportScreen(self, self._save_obj.get('files_path'), self.set_valid_files)

    def set_valid_files(self, path:str, files: list[str] = []) -> None:
        """
        Sets all the following through the [ImportScreen]:
        - self._valid_files.
        - self._number_of_valid_files.
        """
        self._add_to_path_cache(path)
        self._save_obj.update(files_path=path)
        _from_screen = bool(files)
        
        self._valid_files = self._file_viewer.display_files(path, files, _from_screen) 
        self._number_of_valid_files = len(self._valid_files)

        if _from_screen:
            self._update_entry(self._save_obj.get('files_path'))
        
        if self._valid_files:
            self._on_imported()

    def _on_imported(self) -> None:
        """
        Sub-routine for when importing the files is successfully done.
        """
        self._reset_focus()
        self.obs_broadcast(Signal.LOG,self, 
            (f'imported [{self._number_of_valid_files}] files from [{self._save_obj.get('files_path')}].',))

    def _set_data(self) -> None:
        """
        Sets [self._data].
        """
        self._analyze_btn.configure(state=ctk.NORMAL)
        self._data = self._file_viewer.selection()

    def _analyze(self, table_selection: tuple, graph_type: GraphType|None = None) -> None:
        """
        Start the analysis process via signal broadcasting.
        """
        _ids: list[int] = []
        for sel_id in table_selection:
            _id, _file_name = self._file_viewer.get_data(sel_id)
            _ids.append(_id)
            _file_path: str = os.path.join(self._save_obj.get('files_path'), _file_name)
            _in_cache: bool = self._samples_cache.check(_file_path)

            if _in_cache:
                _sample = self._samples_cache.get(_file_path)
            else:
                _sample: Sample = Sample(_file_path)
                self._samples_cache.add(_file_path, _sample)

            self._crnt_sample = _sample

            self.obs_broadcast(Signal.ANALYZE, self, (_sample, self._save_obj, graph_type))
            self.obs_broadcast(Signal.LOG, self, (f'analyzed sample [{_sample.get_name().lower()}].',))

        self._set_interval(_ids)

        self.after(5, self._file_viewer.focus_set)
        if self._save_btn.cget('state') == ctk.DISABLED:
            self._save_btn.configure(state=ctk.NORMAL)
            self._update_export_btn_state(enable=True)

    def _set_interval(self, id_list: list[int]) -> None:
        """
        Sets the [SaveObj] interval for later use by the [export_screen].
        """
        _mode: int = 0
        _interval: list[int] = []
        _consecutive: bool =(np.diff(id_list).cumprod() == 1).all()

        if len(id_list) == 1:
            _mode = 2
            _interval = id_list
        elif len(id_list) == self._number_of_valid_files:
            _interval = id_list
        elif _consecutive:
            _mode = 1
            _interval = [id_list[0], id_list[-1]]
        elif not _consecutive:
            _mode = 2
            _interval = id_list

        self._save_obj.update(interval=(_mode, list(np.array(_interval)-1)))

    def _on_save_btn_pressed(self) -> None:
        """
        Saves a single sample, using:
        - self._crnt_sample.
        - self._save_obj.
        """
        self.cs_save_results(self._crnt_sample, self._save_obj)
        self.obs_broadcast(Signal.LOG, self,
                (f'saved sample [{self._crnt_sample.get_name().lower()}] to [{self._save_obj.get_results_path()}]',))

    def _on_export_btn_pressed(self, use_global_defaults: bool = False) -> None:
        """
        Launches the save all dialogue.
        """
        self._export_popup = ExportScreen(self,
                self._update_export_btn_state, self.save_all, self._save_obj, use_global_defaults)
        self._export_popup.set_limit(self._number_of_valid_files)
        
    def _update_export_btn_state(self, enable: bool = False) -> None:
        """
        Updates the state of the export button in relation to the [ExportScreen].
        """
        if enable and self._export_btn.cget('state') == ctk.DISABLED:
            self._export_btn.configure(state=ctk.NORMAL, image=self._export_btn_icon)
            return
        self._export_btn.configure(state=ctk.DISABLED, image=self._export_btn_dis_icon)

    def update_color_obj(self, color: str) -> None:
        """
        Triggered by an outside signal from [MainPanel].
        """
        self._save_obj.update(color=color)

    def save_all(self, save_obj: SaveObject) -> None:
        """
        Delegated to [ExportScreen].
        """
        self.obs_broadcast(Signal.LOG, self, ('saving all samples...',))

        _trigger_ui_update: Callable[[list[str],int],bool] = lambda list_,cap=20: len(list_) > cap
        
        _index, _interval = save_obj.get('interval') #!config

        def _prep_files_list(index: int, list_: list[str], interval: list[int]) -> list[str]:
            """
            Partition/slice the list of files depending on the index provided, the index is a mode selection of sorts.
            """
            match index:
                case 0:
                    list_ = list_
                case 1:
                    list_ = list_[interval[0]:interval[1]]
                case 2:
                    list_ = [list_[i] for i in interval] #type: ignore
            
            return list_

        _files: list[str] = _prep_files_list(_index, self._valid_files, _interval)
    
        for _ind, file_ in enumerate(_files):
            _path: str = os.path.join(self._save_obj.get('files_path'), file_)
            _sample = Sample(_path)
            self.cs_save_results(_sample, save_obj)
            self.obs_broadcast(Signal.LOG, self,
                               (f'[{_ind}] out of [{len(_files)}] samples saved.',))

            #TODO: is there a better option??, queue/thread??
            if _trigger_ui_update(_files, 0):
                utls.get_root(self).update()
                utls.get_root(self).update_idletasks()
                time.sleep(.001)

        self.obs_broadcast(Signal.LOG, self,
                           (f'saved [{len(_files)}] samples to [{save_obj.get_results_path()}]',))
        self.obs_broadcast(Signal.EXPORTED, self)

    def on_exported(self) -> None:
        """
        Triggered by an outside signal from [MainPanel].
        """
        self._export_popup.on_exported()


class FileViewer(ttk.Treeview, Validator, Observer, HasToolTip):
    """
    ttk.Treeview:
    The class that views and gives the ability to select samples.
    - `display_files`: writes in the samples id and file_name.
    - `get_data`: returns the data.
    """
    def __init__(self, master: ctk.CTkFrame) -> None :
        super().__init__(master)
        
        self._master: ctk.CTkFrame = master

        self._width: int = 0
        self._no_col_width: int = 40
        self._name_col_width: int = 0

        self._tip = None
        self._cid: str = ''
        self._activate_tip: bool = False

        #TODO: mm scale?!, Analyzer is the starting point for this
        self._hdr_strs: list[str] = ['NO', 'File Name']
        self._hdr_tips: list[str] = ['file number', 'sample file name']
        self._hdr_tip_dict: dict[str,str] = {k:v for k,v in zip(self._hdr_strs, self._hdr_tips)}

        # otherwise it wont work as intended!.
        self.bind("<Map>", lambda _: _layout(self.winfo_width()))
        self.bind("<Motion>", lambda event: self._on_mouse_motion(event))
        self.bind("<Leave>", lambda _: self._on_mouse_exited())

        def _layout(width: int) -> None:
            """
            Programmatically set the size of each TreeView column and creates the layout.
            """
            self._width = width
            width -= width%2
            self._name_col_width = self._width - self._no_col_width

            self.configure(style='F_Viewer.Treeview', selectmode="extended",
                        show="headings",
                        columns = ["no", "file_name"])
            
            self.column('no',
                    width=self._no_col_width,
                    minwidth=self._no_col_width, stretch=False, anchor="center")
            self.column('file_name',
                    width=self._name_col_width, minwidth=self._name_col_width)

            self.heading("no", text="NO", anchor="center")
            self.heading("file_name", text="File Name", anchor="w")
            
    def _on_mouse_motion(self, event: tk.Event) -> None:
        """
        To manage to the initialization of the tooltip.
        """
        _pos: tuple[int,int] = (event.x, event.y)
        _area: str = self.identify_region(*_pos)

        if _area == 'heading':
            self._on_mouse_exited()
            _col_id = self.identify_column(_pos[0])
            _hdr_name = self.heading(_col_id)['text']

            if not self._activate_tip:
                self._tip = self.htt_tip(self, self._hdr_tip_dict[_hdr_name], id_=_hdr_name)
                self._tip.on_enter(event)
                self._activate_tip = True

        elif _area == 'cell':
            _cell_id = self.identify_row(event.y)

            if _cell_id != self._cid:
                self._on_mouse_exited(_cell_id)
            _f_name = self.item(_cell_id)['values'][-1]
            if not self._activate_tip:
                self._cid = _cell_id
                self._tip = self.htt_tip(self, _f_name, id_=_f_name)
                self._tip.on_enter(event)
                self._activate_tip = True
        else:
            self._on_mouse_exited()

    def _on_mouse_exited(self, cid: str = '') -> None:
        """
        To disable the tooltip.
        """
        if self._activate_tip:
            self._cid = cid
            if self._tip:
                self._tip.destroy()
            self._activate_tip = False

    def display_files(self, path: str, files: list[str], from_screen: bool) -> list[str]:
        """
        Populates the TreeView with validated samples form the given [path].
        - files: list of file names.
        - from screen: is ImportScreen the caller?.
        - -> valid sample files.
        """
        _valid_files: list[str] = []

        # clear:
        if self.get_children():
            for file_name in self.get_children():
                self.delete(file_name)
        
        # not from_screen means we have a path and vise means we have a list!
        # screen imports are already val_samples validated!
        if not from_screen:
            _files: list[str] = os.listdir(path)
            _valid_files = [file_ for file_ in _files if self.val_samples(path, file_)]
        else:
            for _file in files:
                _valid_files +=  self.val_handle_aio(path, _file)

        self.display(_valid_files)
        
        return _valid_files

    def display(self, valid_files: list[str]) -> None:
        """
        Inserts the data [valid_files] into the table.
        """
        _padding: int = len(f'{len(valid_files)}')

        if not valid_files:
            self.obs_broadcast(Signal.LOG, self,
                    (f'No valid files where found.', LogMsgType.ERROR,))
            return
        for _index, file_ in enumerate(valid_files):
            if _index%2 != 0:
                self.insert("", "end", values=[f'{_index+1:0{_padding}}', file_], tags='odd')
                continue
            self.insert("", "end", values=[f'{_index+1:0{_padding}}', file_])
            
        self.tag_configure('odd', background='#2b2b2b')

    def get_data(self, selection_id: tuple[int, None]) -> tuple[int,str]:
        """
        Retrieves the selected data [selection_id].
        """
        return tuple(self.item(selection_id)["values"]) # type: ignore