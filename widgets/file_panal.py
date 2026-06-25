import os

from collections.abc import Callable
from tkinter import ttk, Event
from PIL import Image

from mixins import CanSave, Defaults, HasToolTip, Validator
from typedefs import GraphType, SaveObject
from popups import ExportScreen
from models import Sample

import customtkinter as ctk

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
        self.files_dir: str = "" #!cnfig
        self.raw_results_folder_name: str = "raw_files" #!cnfig

        #type due to the strange return of the treeview selection method
        self.data: tuple[str,...] = ('',)
        self.number_of_valid_files: int = 0

        self.save_obj: SaveObject = self.df_get(SaveObject)
        self.save_obj_color: str = self.save_obj.color

        self.entry = ctk.CTkEntry(self, placeholder_text="Samples folder path...")
        self.entry.bind("<KeyPress-Return>", lambda _: self._import_files())
        self.entry.bind("<Enter>", lambda _: self.entry.focus_set())
        self.entry.bind("<KeyPress-Escape>", lambda _: self._reset_focus())

        self.import_btn_icon: ctk.CTkImage = ctk.CTkImage(
            Image.open('assets/import.png'), size=(11,11))
        self.file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import",
            image=self.import_btn_icon,
            compound='right',
            command=lambda: self._import_files())
        self.htt_tip(self.file_import_btn, 'import files form the path entered above')

        self.file_viewer: FileViewer = FileViewer(self)
        self.file_viewer.bind(
            "<<TreeviewSelect>>", 
            lambda event: self._set_data(event))
        self.file_viewer.bind("<KeyPress-Return>",
            lambda _: self._analyze(self.data))
        
        self.analyze_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analyze",
            state=ctk.DISABLED,
            command=lambda: self._analyze(self.data))
        self.htt_tip(self.analyze_btn, 'Analayze and preview the sample file selected above')
        
        self.export_btn_icon: ctk.CTkImage = ctk.CTkImage(
            Image.open('assets/upload.png'), size=(11,11))
        self.export_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="export",
            image=self.export_btn_icon,
            compound='right',
            state=ctk.DISABLED, 
            command=lambda: self._on_export_btn_pressed())
        self.export_btn.bind('<Control-Button-1>', lambda _: self._on_export_btn_pressed(True))
        self.htt_tip(self.export_btn, 'a more elaborate saving function\n - [press+Ctrl]: use global defaults')
        
        self.save_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="save",
            state=ctk.DISABLED,
            command=lambda: self._on_save_btn_pressed(self.sample, self.save_obj))
        self.htt_tip(self.save_btn, 'save the anlaysis results of the currently selected sample')

        # layout:
        self.entry.pack(side="top", fill="x", padx=5, pady=5)
        self.file_import_btn.pack(side="top", fill="x", padx=5, pady=5)
        self.file_viewer.pack(side="top", expand=1, fill="both", pady=5, padx=5)
        self.export_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.save_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.analyze_btn.pack(side="bottom", fill="x", padx=5, pady=5)

    def _reset_focus(self) -> None:

        self.master.focus_set()

    def _import_files(self) -> None:
        
        self.files_dir = self.entry.get()
        
        if not os.path.exists(self.files_dir):
            self._set_log_message(f'path [{self.files_dir}] is invalid or doesn\'t exist.', error=True)
        
        self.valid_files: list[str] = self.file_viewer.display_files(self.files_dir)
        self.number_of_valid_files = len(self.valid_files)
        self.export_btn.configure(state=ctk.NORMAL)

        self._reset_focus()
        self._set_log_message(
            f'[{self.number_of_valid_files}] files imported from [{self.files_dir}].')

    def _set_data(self, event: Event) -> None:
        
        self.analyze_btn.configure(state=ctk.NORMAL)
        self.data = self.file_viewer.selection()
        
        if event.state:
            for _type in GraphType:
                    self._analyze(self.data, _type)

    def _analyze(self, table_selection: tuple, graph_type: GraphType|None = None) -> None:

        _file_name: str = self.file_viewer.get_data(table_selection)[-1]#type: ignore
        _file_path: str = os.path.join(self.files_dir, _file_name)

        _sample: Sample = Sample(_file_path)

        self._set_analysis_data(_sample, graph_type)
        self.winfo_toplevel().event_generate("<<FilePanal-analyze>>")
        self._set_log_message(f'[{_sample.get_name().lower()}] analyzed.')

        self.file_viewer.focus_set() #! why broken??
        self.save_btn.configure(state=ctk.NORMAL)
    
    #! here, Continue the sample/file cleanup!!
    def _set_analysis_data(self, sample: Sample, graph_type: GraphType|None) -> None:
        """
        Setting for an outside signal trigger.
        """
        self.sample = sample
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
    
    #? Check the args handiling, it needs to be further trimmed down.
    def _on_save_btn_pressed(self, sample: Sample, save_obj: SaveObject) -> None:
        """
        Saves a single sample.
        """
        self.cs_save_results(sample, self.raw_results_folder_name, save_obj)

        self._set_log_message(f'[{sample.get_name().lower()}] saved...')

    def _on_export_btn_pressed(self, use_global_defaults: bool = False) -> None:
        """
        Launchs the save all dialouge.
        """
        # self._reset_focus()
        self.export_popup: ExportScreen = ExportScreen(self, use_global_defaults)
        self.export_popup.set_color(self.save_obj_color)
        self.export_popup.set_limit(self.number_of_valid_files)

    def _update_save_obj(self, save_obj: SaveObject) -> None:
        
        self.save_obj  = save_obj

    def update_save_obj_color(self, color: str) -> None:
        """
        Triggered by an outside signal.
        """
        self.save_obj.color = color

    def save_all(self) -> None:
        """
        Triggered by an outside signal.
        """
        self._set_log_message('saving all samples...')

        _params: SaveObject = self.export_popup.get_params()
        self._update_save_obj(_params)

        _results_path: str = _params.results_path #!config
        _results_folder_name: str = _params.results_folder_name #!config
        _index, _interval = _params.interval #!cofig

        _files: list[str] = self.valid_files

        def _prep_files_list(index: int, list_: list[str], interval: list[int]) -> list[str]:
            """
            Partition/slice the list of files depending on the index provided, the index is a mode selection of sorts.
            """
            #TODO: centeralize!, moved into a Vlidator mixin

            match index:
                case 0:
                    list_ = list_
                case 1:
                    list_ = list_[interval[0]:interval[1]]
                case 2:
                    list_ = [list_[i] for i in interval]
            
            return list_

        _files = _prep_files_list(_index, _files, _interval)

        for sample_name in _files:
            _path: str = os.path.join(self.files_dir, sample_name)
            _sample = Sample(_path)
            self.cs_save_results(_sample, self.raw_results_folder_name, _params)
        
        _export_path: str = os.path.join(_results_path, _results_folder_name)
        self._set_log_message(f'all samples saved to [{_export_path}]')
        self.winfo_toplevel().event_generate("<<FilePanal-exported>>")

    def on_exported(self) -> None:
        """
        Triggered by an outside signal.
        """
        _path: str = os.path.join(self.export_popup.get_params().results_path, self.export_popup.get_params().results_folder_name)
        self.export_popup.set_results_path(_path)

    def get_analysis_data(self) -> tuple[Sample, GraphType|None]:
        """
        Triggered by an outside signal.
        """
        return (self.sample, self.graph_type)


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

    def display_files(self, path: str) -> list[str]:
        """
        Populates the TreeView with validated samples form the given [path].
        \n\t-> valid sample files.
        """
        if self.get_children():
            [self.delete(i) for i in self.get_children()]

        def validate_files(path: str) -> list[str]:

            _valid_files: list[str] = [file_ for file_ in os.listdir(path) if self.val_samples(path, file_)]
            
            return _valid_files

        _valid_files: list[str] = validate_files(path)
        _padding: int = len(f'{len(_valid_files)}')

        try:
            for _index, file_ in enumerate(_valid_files):
                self.insert("", "end", values=[f'{_index+1:0{_padding}}', file_])
        except FileNotFoundError as e:
            self.master._set_log_message(f'No sample files found; {e}', error=True)
        
        return _valid_files

    def get_data(self, selection_id: tuple[int, None]) -> list[int|str]:
        
        return self.item(selection_id)["values"] # type: ignore