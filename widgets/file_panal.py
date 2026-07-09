import os
from tkinter import Event, ttk

import customtkinter as ctk
from PIL import Image

from mixins import CanSave, Defaults, HasToolTip, Validator
from models import Cache, Sample
from popups import ExportScreen, ImportScreen
from typedefs import GraphType, SaveObject
from utils import utls

# Constants
# colors:
ACTIVE_ENTRY = '#ffffff' #! Base entry class?!
DEFAULT_ENTRY = '#565b5e'

# fonts:
ENTRY_FONT = ('Arial', 16)

# icons:
IMPORT_ICON = Image.open('assets/import.png')
EXPORT_ICON = Image.open('assets/upload.png')

# convension to keep:
# file -> file_name.extension
# sample -> Sample(file_path)
class FilePanal(ctk.CTkFrame, CanSave, Defaults, HasToolTip):
    """
    CTkFrame:
    The class handeling:
        - Entering the samples path [entry].
        - Picking a sample [file_viewer].
        - Analyzing the sample [analyze_btn].
        - Saving the resutls [save_btn].
    """
    def __init__(self, master):
        super().__init__(master)
        #!config = add to a perminent config file!.
        self.configure(corner_radius=0)

        self.master = master
        self.files_dir_path: str = "" #!cnfig
        self.raw_results_dir_name: str = "raw_files" #!cnfig

        #type due to the strange return of the treeview selection method
        self.data: tuple[str,...] = ('',)
        self.valid_files: list[str] = []
        self.number_of_valid_files: int = 0

        self.save_obj: SaveObject = self.df_get(SaveObject)
        self.save_obj_color: str = self.save_obj.color

        # Caching:
        self.samples_cache: Cache = Cache(50)

        # Entry related:
        self.import_icon: ctk.CTkImage = ctk.CTkImage(IMPORT_ICON, size=(11,11))

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
        self.htt_tip(self.analyze_btn, 'Analayze and preview the sample file selected above')
        
        self.export_btn_icon: ctk.CTkImage = ctk.CTkImage(
            EXPORT_ICON, size=(11,11))
        self.export_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="export",
            image=self.export_btn_icon,
            compound='right',
            font=self.entry_font,
            state=ctk.DISABLED, 
            command=lambda: self._on_export_btn_pressed())
        self.export_btn.bind('<Control-Button-1>', lambda _: self._on_export_btn_pressed(True))
        self.htt_tip(self.export_btn, 'open export screen')
        
        self.save_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="save",
            font=self.entry_font,
            state=ctk.DISABLED,
            command=lambda: self._on_save_btn_pressed(self.crnt_sample, self.save_obj))
        self.htt_tip(self.save_btn, 'save the anlaysis results of the currently selected sample')

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
        Behaviour when hovering over [self.entry].
        """
        self.entry.focus_set()
        self.entry.configure(border_color=ACTIVE_ENTRY)
        self.entry.select_to(ctk.END)
        
    def _direct_import(self, path: str) -> None:
        """
        From [self.entry].
        """
        if not os.path.exists(path):
            self._set_log_message(f'path [{path}] is invalid or doesn\'t exist.', error=True)
            return
        
        self.set_valid_files(path)
    
    def _screen_import(self) -> None:
        """
        From the import pop-up screen.
        """
        ImportScreen(self, self.set_valid_files, self.files_dir_path)

    def set_valid_files(self, path:str, files: list[str] = []) -> None:
        """
        Sets all of:
        - self.valid_files.
        - self.number_of_valid_files.
        """
        self.files_dir_path = path
        _from_screen = bool(files)
        
        self.valid_files = self.file_viewer.display_files(path, files, _from_screen) 
        self.number_of_valid_files = len(self.valid_files)

        if _from_screen:
            self.entry.delete(0, ctk.END)
            self.entry.insert(0, self.files_dir_path)
        self._on_imported()

    def _on_imported(self) -> None:
        """
        Sub-routine for importing files is Done.
        """
        self.export_btn.configure(state=ctk.NORMAL)

        self._reset_focus()
        self._set_log_message(
            f'[{self.number_of_valid_files}] files imported from [{self.files_dir_path}].')

    def _set_data(self) -> None:
        
        self.analyze_btn.configure(state=ctk.NORMAL)
        self.data = self.file_viewer.selection()

    def _analyze(self, table_selection: tuple, graph_type: GraphType|None = None) -> None:

        _file_name: str = self.file_viewer.get_data(table_selection)[-1] #type: ignore
        _file_path: str = os.path.join(self.files_dir_path, _file_name)
        _in_cache: bool = self.samples_cache.check(_file_path)

        if _in_cache:
            _sample = self.samples_cache.get(_file_path) #type: ignore
        else:
            _sample: Sample = Sample(_file_path)
            self.samples_cache.add(_file_path, _sample)

        #! Signal!:
        self._set_analysis_data(_sample, graph_type)
        self.winfo_toplevel().event_generate("<<FilePanal-analyze>>")
        self._set_log_message(f'[{_sample.get_name().lower()}] analyzed.')

        self.after(5, self.file_viewer.focus_set)
        if self.save_btn.cget('state') == ctk.DISABLED:
            self.save_btn.configure(state=ctk.NORMAL)

    def _set_analysis_data(self, sample: Sample, graph_type: GraphType|None) -> None:
        """
        Setting for an outside signal trigger.
        """
        self.crnt_sample = sample
        self.graph_type = graph_type

    def _set_log_message(self, massage: str, error: bool = False) -> None:
        """
        Setting for an outside signal trigger.
        """
        self.log_massage: str = massage if not error else '<!> Error: '+ massage
        self.winfo_toplevel().event_generate("<<FilePanal-log>>")

    def get_log_massage(self) -> str:
        """
        Returns the logged massage, triggered by an outside signal.
        """
        return self.log_massage
    
    def _on_save_btn_pressed(self, sample: Sample, save_obj: SaveObject) -> None:
        """
        Saves a single sample.
        """
        self.cs_save_results(sample, self.raw_results_dir_name, save_obj)
        self._set_log_message(f'[{sample.get_name().lower()}] saved...')

    def _on_export_btn_pressed(self, use_global_defaults: bool = False) -> None:
        """
        Launchs the save all dialouge.
        """
        self.export_popup: ExportScreen = ExportScreen(self, use_global_defaults)
        self.export_popup.set_color(self.save_obj_color)
        self.export_popup.set_limit(self.number_of_valid_files)

    def _update_save_obj(self, save_obj: SaveObject) -> None:
        """
        Updates this classe's [save_obj].
        """
        self.save_obj  = save_obj

    def update_save_obj_color(self, color: str) -> None:
        """
        Triggered by an outside signal from [MainPanal].
        """
        self.save_obj.color = color

    def save_all(self) -> None:
        """
        Triggered by an outside signal from [MainPanal].
        """
        self._set_log_message('saving all samples...')

        _params: SaveObject = self.export_popup.get_params()
        self._update_save_obj(_params)

        _files: list[str] = self.valid_files

        _results_path: str = _params.results_path #!config
        _results_folder_name: str = _params.results_folder_name #!config
        _index, _interval = _params.interval #!cofig

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
                    list_ = [list_[i] for i in interval]
            
            return list_

        _files = _prep_files_list(_index, _files, _interval)

        for file_ in _files:
            _path: str = os.path.join(self.files_dir_path, file_)
            _sample = Sample(_path)
            self.cs_save_results(_sample, self.raw_results_dir_name, _params)
        
        _export_path: str = os.path.join(_results_path, _results_folder_name)
        self._set_log_message(f'all samples saved to [{_export_path}]')
        self.winfo_toplevel().event_generate("<<FilePanal-exported>>")

    def on_exported(self) -> None:
        """
        Triggered by an outside signal from [MainPanal].
        """
        _save_obj: SaveObject = self.export_popup.get_params()
        _path: str = os.path.join(_save_obj.results_path, _save_obj.results_folder_name)
        self.export_popup.set_results_path(_path)

    def get_analysis_data(self) -> tuple[Sample, GraphType|None]:
        """
        Triggered by an outside signal from [MainPanal].
        """
        return (self.crnt_sample, self.graph_type)


class FileViewer(ttk.Treeview, Validator):
    """
    ttk.Treeview:
    The class that views and gives the ability to select samples.
    - display_files(dir: str) writes in the samples id and file_name.
    - get_data(selection_id: str) -> [id: int, sample_file_name: str].
    """
    def __init__(self, master: FilePanal) -> None :
        super().__init__(master)

        self.master: FilePanal = master

        # Styling:
        _row_style = ttk.Style()
        _row_style.theme_use('default')
        _row_style.configure('Treeview',
            foreground='white',
            background='#2b2b2b',
            bordercolor='#1f6aa5',
            borderwidth=0,
            rowheight=25, font=('Arial', 12),
            fieldbackground='#2b2b2b')
        _row_style.map('Treeview')

        _header_style = ttk.Style()
        _header_style.configure('Treeview.Heading', 
            relief='flat',
            foreground='white',
            background='#1f6aa5',
            bordercolor='#1f6aa5',
            font=('Arial', 14, 'bold'))
        _header_style.map('Treeview.Heading',
            background=[('active', '#144870')])

        self.configure(style='Treeview', selectmode="browse",
                       show="headings",
                       columns = ["no", "file_name"])
        
        self.column('no', width=40, minwidth=40, stretch=False, anchor="center")
        self.column('file_name', width=194, minwidth=190, stretch=False)

        self.heading("no", text="NO", anchor="center")
        self.heading("file_name", text="File Name", anchor="w")

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
        
        if valid_files:
            for _index, file_ in enumerate(valid_files):
                self.insert("", "end", values=[f'{_index+1:0{_padding}}', file_])
        else:
            self.master._set_log_message(f'No sample where files found.', error=True)
        

    def get_data(self, selection_id: tuple[int, None]) -> list[int|str]:
        
        return self.item(selection_id)["values"] # type: ignore