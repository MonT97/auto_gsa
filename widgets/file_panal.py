import os

from typedefs import GraphType, FileFormat
from helpers import Analyzer, Plotter
from tkinter import ttk, Event
from models import Sample

import matplotlib.pyplot as plt
import customtkinter as ctk
import pandas as pd

class FilePanal(ctk.CTkFrame):
    '''
    CTkFrame:
    The class handeling:
        - Picking the samples path [entry].
        - Picking a sample [file_viewer].
        - Analyzing said sample [analyze_btn].
        - Saving said analysis resutls [save_btn].
    '''
    def __init__(self, master):
        super().__init__(master)
        
        self.master = master
        self.samples_files_dir: str = ""
        self.sample: Sample = Sample()
        self.data: tuple = ()

        self.supported_formats: list[str] = [_format.value for _format in FileFormat]

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter the samples folder path...")
        self.entry.bind("<KeyPress-Return>", command= lambda _: self._import_files())
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
        self.save_all_btn: ctk.CTkButton = ctk.CTkButton(
            self,
            text="save all",
            state=ctk.DISABLED,
            command=lambda: self._save_all())
        self.save_btn: ctk.CTkButton = ctk.CTkButton(
            self,
            text="save results",
            state=ctk.DISABLED,
            command=lambda: self._save_results(self.sample))

        self.entry.pack(side="top", fill="x", padx=5, pady=5)
        self.file_import_btn.pack(side="top", fill="x", padx=5, pady=5)
        self.samples_file_viewer.pack(side="top", fill="x", pady=5, padx=5)
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

    def _set_data(self, selection: tuple, event: Event=None) -> None: # type: ignore
        
        self.analyze_btn.configure(state=ctk.NORMAL)
        self.data = selection
        
        if event.state:
            for _type in GraphType:
                self._analyze(self.data, _type)

    def _analyze(self, table_selection: tuple, graph_type: GraphType|None = None):

        # self.master.event_generate("<<FilePanalEvent>>") #! see why this doesn't work?

        sample_file_name = self.samples_file_viewer.get_data(table_selection)[-1]
        sample_data = pd.read_excel(f"{self.samples_files_dir}\\{sample_file_name}")

        self.sample: Sample = Sample(sample_file_name, sample_data) # type: ignore

        self.analysis_panal.write(self.sample, graph_type)
        self.analysis_panal.draw_graphs(self.sample, graph_type)

        self.samples_file_viewer.focus_set() #! why broken??
        self.save_btn.configure(state=ctk.NORMAL)
    
    def _save_results(self, sample: Sample):
        
        self.analysis_panal.save_data(sample, self.samples_files_dir)

    def _save_all(self) -> None:

        files: list[str] = os.listdir(self.samples_files_dir)
        files = [_file for _file in files if _file.split(".")[-1] in self.supported_formats]

        fig, ax = plt.subplots(4, 2, figsize=(9,12))

        itr: int = 0
        graphs_per_page: int = 2
        page_num: int = 1

        for ind, f_name in enumerate(files):

            name: str = f_name
            f_path: str = os.path.join(self.samples_files_dir, f_name)
            data: pd.DataFrame = pd.read_excel(f_path)
            sample: Sample = Sample(name ,data)
            cum_points, hist_points = [Analyzer(sample.get_data()).get_plot_data(i) for i in GraphType]
            Plotter(hist_points[0], hist_points[1], hist_points[2],ax[itr,0], GraphType.HIST)
            Plotter(cum_points[0], cum_points[1], cum_points[2],ax[itr,1], GraphType.CUM)
            itr+=1

            if ind == 3 and len(files)%3 != 0:

                self.analysis_panal.save_data(sample, self.samples_files_dir, page_num, fig)
                fig, ax = plt.subplots(4, 2, figsize=(8,11))
                itr = 0
                page_num+=1

        self.analysis_panal.save_data(sample, self.samples_files_dir, page_num, fig)
    
    def set_analysis_panal(self, analysis_panal) -> None:
        '''
        Called by the analysis panal.
        '''
        self.analysis_panal = analysis_panal


class FileViewer(ttk.Treeview):
    '''
    Treeview:
    The class that views and gives the ability to select samples.
    - display_files(dir: str) writes in the samples id and file_name.
    - get_data(selection_id: str) -> [id: int, sample_file_name: str].
    '''
    def __init__(self, master: FilePanal) -> None :
        super().__init__(master)

        self.formats: list[str] = master.supported_formats

        row_style = ttk.Style()
        row_style.theme_use('default')
        row_style.configure('Treeview',
            foreground='white',
            background='#333333',
            bordercolor='#1f6aa5',
            borderwidth=0,
            rowheight=25, font=('Arial', 12),
            fieldbackground='#333333')
        row_style.map('Treeview')
        
        header_style = ttk.Style()
        header_style.configure('Treeview.Heading', 
            relief='flat',
            foreground='white',
            background='#1f6aa5',
            bordercolor='#1f6aa5',
            font=('Arial', 14, 'bold'))
        header_style.map('Treeview.Heading',
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
        supported: function = lambda file_: file_.split(".")[-1] in self.formats
        supported_files: list[str] = [file_ for file_ in os.listdir(_dir) if supported(file_)]
        padding: int = len(str(len(supported_files)))+1

        try:
            for index, file_ in enumerate(supported_files):
                self.insert("", "end", values=[f'{index+1:0{padding}}', file_])
        except FileNotFoundError as e:
            raise e
            #TODO: add an error logging capacity if no files are found len(supp_files==0)
            pass

    def get_data(self, selection_id: tuple[int, None]) -> list[int|str]:

        self.item(selection_id[0])
        return self.item(selection_id)["values"] # type: ignore