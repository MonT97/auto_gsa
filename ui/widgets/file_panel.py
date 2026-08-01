import os
import time
from tkinter import ttk
from typing import Callable, Final

import customtkinter as ctk
from PIL import Image

from mixins import CanSave, Defaults, HasToolTip, Observer, Validator
from models import Cache, Sample
from popups import ExportScreen, ImportScreen
from typedefs import GraphType, LogMsgType, SaveObject, Signal
from utils import utls

# Constants
# colors:
DEFAULT_GRAPH_COLOR: Final[str] = '#1f7bb4'
ACTIVE_ENTRY: Final[str] = '#ffffff' #! Base entry class?!
DEFAULT_ENTRY: Final[str] = '#565b5e'

# fonts:
ENTRY_FONT: Final[tuple[str, int]] = ('Arial', 16)

# icons:
ICON_SIZE: Final[tuple[int,int]] = (15,15)
IMPORT_ICON: Final = Image.open('assets/import.png')
EXPORT_ICON: Final = Image.open('assets/upload.png')
EXPORT_DIS_ICON: Final = Image.open('assets/upload_dis.png')


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

        self.master = master

        # pass around data holder.
        self.save_obj: SaveObject = self.df_get(SaveObject)

        #type due to the strange return of the treeview selection method
        self.data: tuple[str,...] = ('',)
        self.valid_files: list[str] = []
        self.number_of_valid_files: int = 0

        # Caching:
        self.samples_cache: Cache = Cache(50)

        # Entry related:
        self.import_icon: ctk.CTkImage = ctk.CTkImage(IMPORT_ICON, size=ICON_SIZE)

        self.entry_font = ctk.CTkFont(*ENTRY_FONT)

        self.entry_frame: ctk.CTkFrame = ctk.CTkFrame(self, height=30)

        self.entry = ctk.CTkEntry(self.entry_frame,
            border_color=DEFAULT_ENTRY,
            placeholder_text="sample files folder path...")
        self.entry.bind("<KeyPress-Return>", lambda _: self._direct_import(self.entry.get()))
        self.entry.bind("<Enter>", lambda _: self._on_entry_active())
        self.entry.bind("<KeyPress-Escape>", lambda _: self._reset_focus())
        self.htt_tip(self.entry, 'path to import from\npress [Enter/Return] to quick import')
        utls.bg_transparent(self.entry)

        self.file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import",
            image=self.import_icon,
            compound='right',
            font=self.entry_font,
            command=lambda: self._screen_import())
        self.htt_tip(self.file_import_btn, 'open import screen')

        # Viewer:
        self.file_viewer: FileViewer = FileViewer(self)
        self.file_viewer.bind("<<TreeviewSelect>>", lambda _: self._set_data())
        self.file_viewer.bind("<KeyPress-Return>", 
                lambda _: self._analyze(self.data))
        self.file_viewer.bind("<Leave>", lambda _: self._reset_focus())
        
        # Lower buttons:
        self.analyze_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analyze",
            font=self.entry_font,
            state=ctk.DISABLED,
            command=lambda: self._analyze(self.data))
        self.htt_tip(self.analyze_btn, 'Analyze and preview the sample file selected above')
        
        self.save_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="save",
            font=self.entry_font,
            state=ctk.DISABLED,
            command=lambda: self._on_save_btn_pressed(self.crnt_sample, self.save_obj))
        self.htt_tip(self.save_btn, 'save the analysis results of the currently selected sample')

        self.export_btn_icon: ctk.CTkImage = ctk.CTkImage(
            EXPORT_ICON, size=ICON_SIZE)
        self.export_btn_dis_icon: ctk.CTkImage = ctk.CTkImage(
            EXPORT_DIS_ICON, size=ICON_SIZE)
        self.export_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="export",
            image=self.export_btn_dis_icon,
            compound='right',
            font=self.entry_font,
            state=ctk.DISABLED, 
            command=lambda: self._on_export_btn_pressed())
        self.export_btn.bind('<Control-Button-1>', lambda _: self._on_export_btn_pressed(True))
        self.htt_tip(self.export_btn, 'open export screen')        

        # layout:
        self.entry.pack(side='top', fill='x')
        self.entry_frame.pack(side="top", fill="x", padx=5, pady=(5,0))

        self.file_import_btn.pack(side="top", fill="x", padx=5, pady=(5,5))
        self.file_viewer.pack(side="top", expand=1, fill="both", padx=5, pady=(5,5))
        self.export_btn.pack(side="bottom", fill="x", padx=5, pady=(5,5))
        self.save_btn.pack(side="bottom", fill="x", padx=5, pady=(5,0))
        self.analyze_btn.pack(side="bottom", fill="x", padx=5, pady=(5,0))

    def _reset_focus(self) -> None:
        """
        Resets the focus to master from [self.entry].
        """
        self.entry.configure(border_color=DEFAULT_ENTRY)
        self.master.focus_set()

    def _on_entry_active(self) -> None:
        """
        Behavior when hovering over [self.entry].
        """
        self.entry.focus_set()
        self.entry.configure(border_color=ACTIVE_ENTRY)
        self.entry.select_range('0', ctk.END)
        
    def _direct_import(self, path: str) -> None:
        """
        From [self.entry].
        """
        self.save_obj.files_path = path
        if not os.path.exists(path):
            self.obs_broadcast(Signal.LOG, self,
                    (f'path [{path}] is invalid or doesn\'t exist.', LogMsgType.ERROR))
            return
        
        self.set_valid_files(path)
    
    def _screen_import(self) -> None:
        """
        From the import pop-up screen.
        """
        ImportScreen(self, self.save_obj.files_path, self.set_valid_files)

    def set_valid_files(self, path:str, files: list[str] = []) -> None:
        """
        Sets all of:
        - self.valid_files.
        - self.number_of_valid_files.
        """
        self.save_obj.files_path = path
        _from_screen = bool(files)
        
        self.valid_files = self.file_viewer.display_files(path, files, _from_screen) 
        self.number_of_valid_files = len(self.valid_files)

        if _from_screen:
            self.entry.delete(0, ctk.END)
            self.entry.insert(0, self.save_obj.files_path)
        
        if self.valid_files:
            self._on_imported()

    def _on_imported(self) -> None:
        """
        Sub-routine for importing files is successfully done.
        """
        self.export_btn.configure(state=ctk.NORMAL, image=self.export_btn_icon)
        self._reset_focus()
        self.obs_broadcast(Signal.LOG, self, 
            (f'imported [{self.number_of_valid_files}] files from [{self.save_obj.files_path}].',))

    def _set_data(self) -> None:
        
        self.analyze_btn.configure(state=ctk.NORMAL)
        self.data = self.file_viewer.selection()

    def _analyze(self, table_selection: tuple, graph_type: GraphType|None = None) -> None:

        _file_name: str = self.file_viewer.get_data(table_selection)[-1] #type: ignore
        _file_path: str = os.path.join(self.save_obj.files_path, _file_name)
        _in_cache: bool = self.samples_cache.check(_file_path)

        if _in_cache:
            _sample = self.samples_cache.get(_file_path) #type: ignore
        else:
            _sample: Sample = Sample(_file_path)
            self.samples_cache.add(_file_path, _sample)

        self._set_analysis_data(_sample, graph_type)
        self.obs_broadcast(Signal.ANALYZE, self, (self.crnt_sample, self.save_obj))
        self.obs_broadcast(Signal.LOG, self, (f'analyzed sample [{_sample.get_name().lower()}].',))

        self.after(5, self.file_viewer.focus_set)
        if self.save_btn.cget('state') == ctk.DISABLED:
            self.save_btn.configure(state=ctk.NORMAL)

    def _set_analysis_data(self, sample: Sample, graph_type: GraphType|None) -> None:
        """
        Setting for an outside signal trigger.
        """
        self.crnt_sample = sample
        self.graph_type = graph_type
    
    def _on_save_btn_pressed(self, sample: Sample, save_obj: SaveObject) -> None:
        """
        Saves a single sample.
        """
        self.cs_save_results(sample, save_obj)
        self.obs_broadcast(Signal.LOG, self,
                (f'saved sample [{sample.get_name().lower()}] to [{save_obj.get_results_path()}]',))

    def _on_export_btn_pressed(self, use_global_defaults: bool = False) -> None:
        """
        Launches the save all dialogue.
        """
        self.export_popup = ExportScreen(self, self.save_all, self.save_obj, use_global_defaults)
        self.export_popup.set_limit(self.number_of_valid_files)

    def update_color_obj(self, color: str) -> None:
        """
        Triggered by an outside signal from [MainPanel].
        """
        self.save_obj.color = color

    def save_all(self, save_obj: SaveObject) -> None:
        """
        Triggered by an outside signal from [MainPanel].
        """
        self.obs_broadcast(Signal.LOG, self, ('saving all samples...',))

        _trigger_ui_update: Callable[[list[str],int],bool] = lambda list_,cap=20: len(list_) > cap
        
        _index, _interval = save_obj.interval #!config

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

        _files: list[str] = _prep_files_list(_index, self.valid_files, _interval)
    
        for _ind, file_ in enumerate(_files):
            _path: str = os.path.join(self.save_obj.files_path, file_)
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
        self.export_popup.on_exported()


class FileViewer(ttk.Treeview, Validator, Observer, HasToolTip):
    """
    ttk.Treeview:
    The class that views and gives the ability to select samples.
    - display_files(dir: str) writes in the samples id and file_name.
    - get_data(selection_id: str) -> [id: int, sample_file_name: str].
    """
    def __init__(self, master: FilePanel) -> None :
        super().__init__(master)
        
        self.master: FilePanel = master

        self.width: int = 0
        self.no_col_width: int = 40
        self.name_col_width: int = 0

        # otherwise it wont work as intended!.
        self.bind("<Map>", lambda _: _set_element_width(self.winfo_width()))

        def _set_element_width(width: int) -> None:
            """
            Programmatically set the size of each TreeView column.
            """
            self.width = width
            width -= width%2
            self.name_col_width = self.width - self.no_col_width

            _layout()

        def _layout() -> None:
            self.configure(style='F_Viewer.Treeview', selectmode="browse",
                        show="headings",
                        columns = ["no", "file_name"])
            
            self.column('no',
                    width=self.no_col_width,
                    minwidth=self.no_col_width, stretch=False, anchor="center")
            self.column('file_name',
                    width=self.name_col_width, minwidth=self.name_col_width)

            self.heading("no", text="NO", anchor="center")
            self.heading("file_name", text="File Name", anchor="w")

        self.configure(style='F_Viewer.Treeview', show="headings")

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
            _valid_files = [
                file_ for file_ in _files if self.val_samples(path, file_)
                ]
        else:
            for _file in files:
                _valid_files +=  self.val_handle_aio(path, _file)

        self.display(_valid_files)
        
        return _valid_files

    def display(self, valid_files: list[str]) -> None:

        _padding: int = len(f'{len(valid_files)}')
        if not valid_files:
            self.obs_broadcast(Signal.LOG, self,
                    (f'No valid files where found.', LogMsgType.ERROR,))
            return
        for _index, file_ in enumerate(valid_files):
            self.insert("", "end", values=[f'{_index+1:0{_padding}}', file_])

    def get_data(self, selection_id: tuple[int, None]) -> list[int|str]:
        
        return self.item(selection_id)["values"] # type: ignore