import os

from typedefs import GraphType, FileFormat
from helpers import Analyzer, Plotter
from collections.abc import Callable
from tkinter import ttk, Event
from models import Sample

import matplotlib.pyplot as plt
import customtkinter as ctk
import pandas as pd

class FilePanal(ctk.CTkFrame):
    '''
    CTkFrame:
    The class handeling:
        - Entering the samples path [entry].
        - Picking a sample [file_viewer].
        - Analyzing the sample [analyze_btn].
        - Saving the resutls [save_btn].
    '''
    def __init__(self, master):
        super().__init__(master)
        
        self.master = master
        self.samples_files_dir: str = "" #!cnfig
        self.results_folder_name: str = "analysis_results" #!cnfig
        self.raw_results_folder_name: str = "raw_files" #!cnfig
        self.data: tuple[int,] = (0,)

        self.supported_formats: list[str] = [_format.value for _format in FileFormat]

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter the samples folder path...")
        self.entry.bind("<KeyPress-Return>", lambda _: self._import_files())
        self.entry.bind("<Enter>", lambda _: self.entry.focus_set())
        self.entry.bind("<KeyPress-Escape>", lambda _: self._reset_focus())

        self.file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import files",
            command=lambda: self._import_files())

        self.samples_file_viewer: FileViewer = FileViewer(self)
        self.samples_file_viewer.bind(
            "<<TreeviewSelect>>", 
            lambda event: self._set_data(self.samples_file_viewer.selection(), event))
        self.samples_file_viewer.bind("<KeyPress-Return>",
            lambda _: self._analyze(self.data))
        
        self.analyze_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analyze",
            state=ctk.DISABLED,
            command=lambda: self._analyze(self.data))
        
        self.save_all_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="save all",
            state=ctk.DISABLED,
            command=lambda: self._save_all())
        
        self.save_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="save results",
            state=ctk.DISABLED,
            command=lambda: self._save_results(self.sample, fmt=FileFormat.EXCEL))

        self.entry.pack(side="top", fill="x", padx=5, pady=5)
        self.file_import_btn.pack(side="top", fill="x", padx=5, pady=5)
        self.samples_file_viewer.pack(side="top", expand=1, fill="both", pady=5, padx=5)
        self.save_all_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.save_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.analyze_btn.pack(side="bottom", fill="x", padx=5, pady=5)

    def _reset_focus(self) -> None:

        self.master.focus_set()

    def _import_files(self) -> None:
        
        self.samples_files_dir: str = self.entry.get()
        self.samples_file_viewer.display_files(self.samples_files_dir)
        self.save_all_btn.configure(state=ctk.NORMAL)

        self._reset_focus()

    def _set_data(self, selection: tuple, event: Event) -> None:
        
        self.analyze_btn.configure(state=ctk.NORMAL)
        self.data = selection
        
        if event.state:
            for _type in GraphType:
                    self._analyze(self.data, _type)

    def _analyze(self, table_selection: tuple, graph_type: GraphType|None = None):

        _sample_file_name: str = self.samples_file_viewer.get_data(table_selection)[-1]#type: ignore
        _sample_file_path: str = os.path.join(self.samples_files_dir, _sample_file_name)

        _sample: Sample = Sample(_sample_file_path)

        self._set_analysis_data(_sample, graph_type)
        self.winfo_toplevel().event_generate("<<FilePanal-analyze>>")

        self.samples_file_viewer.focus_set() #! why broken??
        self.save_btn.configure(state=ctk.NORMAL)
    
    def _set_analysis_data(self, sample: Sample, graph_type: GraphType|None) -> None:

        self.sample = sample
        self.graph_type = graph_type

    #TODO: this needs a redo, stay here??, sperate class, who knows?!    
    def _save_results(self,
                      sample: Sample, prfx: str = 'result_', rounding: int = 3,
                      fmt: FileFormat = FileFormat.CSV) -> None:

        _result_file_name: str = prfx+sample.get_name().lower()
        _results_dir: str = os.path.join(self.samples_files_dir, self.results_folder_name)
        _raw_results_dir: str = os.path.join(_results_dir, self.raw_results_folder_name) #!rawThing

        _file_path: str = os.path.join(_results_dir, _result_file_name)
        _raw_file_path: str = os.path.join(_raw_results_dir, _result_file_name)

        _sample_data: pd.DataFrame = sample.get_data()

        _ana: Analyzer = Analyzer(_sample_data)
        _stats_sheet_name: str = f'stats({_ana.get_method()})'
        _stats = _ana.get_stats().to_frame()
        _interp = _ana.get_interpretation().to_frame()

        if not os.path.exists(_results_dir):
            os.mkdir(_results_dir)
        
        if not os.path.exists(_raw_results_dir):
            os.mkdir(_raw_results_dir)
        
        with pd.ExcelWriter(f'{_file_path}.xlsx', engine='openpyxl', mode='w') as writer:
            _sample_data.to_excel(writer, index=False, sheet_name='data')
            _stats.to_excel(writer, index=False, float_format=f'%.{rounding}f',
                            merge_cells=False, sheet_name=_stats_sheet_name)
            _interp.to_excel(writer, index=False,
                            merge_cells=False, startrow=_stats.shape[0]+2,
                            sheet_name=_stats_sheet_name)

        _sample_data.to_csv(f'{_raw_file_path}.csv', index=False)

        for _type in GraphType:
            _graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}
            _title: str = _graph_names[_type]
            _graph_file_name: str = f'{sample.get_name().lower()}_{_title.lower().replace(' ', '_')}'
            _graph_file_path: str = os.path.join(_results_dir, _graph_file_name)
            _raw_graph_file_path: str = os.path.join(_raw_results_dir, _graph_file_name)
            
            _fig, _ax = plt.subplots()
            _fig.set_layout_engine('constrained')
            _x, _y, _points = _ana.get_plot_data(_type)
            Plotter(_x, _y, _points, _ax, _type)
            _ax.set_title(f'{sample.get_name()}\n{_title}')
            _fig.savefig(_graph_file_path+'.png', dpi=300, format='png')
            _fig.savefig(_raw_graph_file_path+'.svg', dpi=300, format='svg')
            plt.close()
            
        print(f'[{sample.get_name().lower()}] saved...') #TODO: log

    def _save_all(self) -> None:

        files: list[str] = os.listdir(self.samples_files_dir)
        files = [_file for _file in files if _file.split(".")[-1] in self.supported_formats]

        for sample_name in files:
            _path: str = os.path.join(self.samples_files_dir, sample_name)
            _sample = Sample(_path)
            self._save_results(_sample)
        
        print('all samples saved...') #TODO: log

    def get_analysis_data(self) -> tuple[Sample, GraphType|None]:
        '''
        Triggered by an outside signal.
        '''
        return (self.sample, self.graph_type)


class FileViewer(ttk.Treeview):
    '''
    ttk.Treeview:
    The class that views and gives the ability to select samples.
    - display_files(dir: str) writes in the samples id and file_name.
    - get_data(selection_id: str) -> [id: int, sample_file_name: str].
    '''
    def __init__(self, master: FilePanal) -> None :
        super().__init__(master)

        self.formats: list[str] = master.supported_formats

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

    def display_files(self, _dir: str) -> None:
        
        if self.get_children():
            [self.delete(i) for i in self.get_children()]

        #TODO: add format support read from a config maybe?!
        _supported: Callable = lambda file_: file_.split(".")[-1] in self.formats
        _supported_files: list[str] = [file_ for file_ in os.listdir(_dir) if _supported(file_)]
        _padding: int = len(str(len(_supported_files)))+1

        try:
            for _index, file_ in enumerate(_supported_files):
                self.insert("", "end", values=[f'{_index+1:0{_padding}}', file_])
        except FileNotFoundError as e:
            raise e
            #TODO: add an error logging capacity if no files are found len(supp_files==0)
            pass

    def get_data(self, selection_id: tuple[int, None]) -> list[int|str]:
        
        return self.item(selection_id)["values"] # type: ignore