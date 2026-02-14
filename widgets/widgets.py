import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typedefs import GraphType, FileFormat, PlotData
from helpers import Analyzer, Plotter
from matplotlib.axes import Axes
from tkinter import ttk, Event
from models import Sample

import matplotlib.pyplot as plt
import customtkinter as ctk
import tkinter as tk
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
    def __init__(self, master: ctk.CTk, analysis_panal):
        super().__init__(master)

        self.analysis_panal = analysis_panal
        self.samples_files_dir: str = ""
        self.sample: Sample = None #type: ignore
        self.data: tuple = ()

        self.supported_formats: list[str] = [_format.value for _format in FileFormat]

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter the samples folder path...")
        self.entry.bind("<KeyPress-Return>", command= lambda _event: self.import_files())
        self.entry.bind('<Enter>', lambda _event: self.entry.focus_set())
        self.entry.bind('<KeyPress-Escape>', lambda _event: self.reset_focus())
        self.file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import files",
            command=lambda: self.import_files())

        self.samples_file_viewer: FileViewer = FileViewer(self)

        self.samples_file_viewer.bind(
            "<<TreeviewSelect>>", 
            lambda event: self.set_data(self.samples_file_viewer.selection(), event))
        self.samples_file_viewer.bind("<KeyPress-Return>",
            lambda _event: self.analyze(self.data))

        self.analyze_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analyze",
            state="disabled",
            command=lambda: self.analyze(self.data, GraphType.CUM))
        self.save_all_btn: ctk.CTkButton = ctk.CTkButton(
            self,
            text="save all",
            state="disabled",
            command=lambda: self.save_all())
        self.save_btn: ctk.CTkButton = ctk.CTkButton(
            self,
            text="save results",
            state="disabled",
            command=lambda: self.save_results(self.sample))

        self.entry.pack(side="top", fill="x", padx=5, pady=5)
        self.file_import_btn.pack(side="top", fill="x", padx=5, pady=5)
        self.samples_file_viewer.pack(side="top", fill="x", pady=5, padx=5)
        self.save_all_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.save_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.analyze_btn.pack(side="bottom", fill="x", padx=5, pady=5)
    
    def reset_focus(self) -> None:

        self.master.focus_set()

    def import_files(self) -> None:

        self.samples_files_dir: str = self.entry.get()
        self.samples_file_viewer.display_files(self.samples_files_dir)
        self.save_all_btn.configure(state="normal")

        self.reset_focus()

    def set_data(self, selection: tuple, event: Event=None): # type: ignore
        
        self.analyze_btn.configure(state="normal")
        self.data = selection
        
        if event.state:
            for _type in GraphType:
                self.analyze(self.data, _type)

    def analyze(self, table_selection: tuple, graph_type: GraphType|None = None):

        sample_file_name = self.samples_file_viewer.get_data(table_selection)[-1]
        sample_data = pd.read_excel(f"{self.samples_files_dir}\\{sample_file_name}")

        self.sample: Sample = Sample(sample_file_name, sample_data) # type: ignore

        self.analysis_panal.write(self.sample, graph_type)
        self.analysis_panal.draw_graphs(self.sample, graph_type)

        self.samples_file_viewer.focus_set() #! why broken??
        self.save_btn.configure(state="normal")
    
    def save_results(self, sample: Sample):
        
        self.analysis_panal.save_data(sample, self.samples_files_dir)

    def save_all(self) -> None:

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

        #TODO: add format support
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


class AnalysisPanal(ctk.CTkFrame):
    '''
        CTkFrame:
        The class that handels viewing and analyzing the data.
            - display the sample graphs [gaph_panal: ctk.CTkLabel].
            - display the sample data and the analysis result [data_panal: AnalysisBook]
    '''
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)

        self.current_sample: Sample = Sample()

        self.graph_panal: GraphPanal = GraphPanal(self)
        self.data_panal: DataPanal = DataPanal(self)

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.rowconfigure(0, weight=5, uniform='a')
        self.rowconfigure(1, weight=4, uniform='a')

        self.graph_panal.grid(
            column=0, columnspan=2, row=0, rowspan=1,
            padx=5, pady=5,sticky='nsew')
        self.data_panal.grid(
            column=0, columnspan=2, row=1, rowspan=1,
            padx=5, pady=5, sticky='nsew')

    def create_analyzer(self, sample: Sample) -> None:
        if self.current_sample != sample:
            self.analyzer: Analyzer = Analyzer(sample.get_data())

    def draw_graphs(self, sample: Sample, graph_type: GraphType|None = None) -> None:
        self.create_analyzer(sample)
        #? is this the best place for this? NO
        self.graph_panal.draw_graphs(self.analyzer, sample.get_name(), graph_type)      

    def write(self, sample: Sample, graph_type: GraphType) -> None:
        self.create_analyzer(sample)
        self.data_panal.write(self.analyzer, sample, graph_type)


class GraphPanal(ctk.CTkFrame):
    '''
        CTkFrame:
        View the resulting graphs
    '''
    #TODO add the ability to change the graph color, maybe only during saves as this is a preview!?
    def __init__(self, master: AnalysisPanal) -> None:
        super().__init__(master)

        self.graphs: list[Axes] = []
        self.graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')

    def draw_graphs(self, analyzer: Analyzer, sample_name: str, graph_type: GraphType|None) -> None:
        '''
            Layout the graphs
            - graph_type = None -> layout all the graphs in enums.GraphType
        '''
        #? resetting the layout!
        for i in self.grid_slaves():
            i.grid_forget()

        if graph_type:
            graph = self.generate_graph(analyzer.get_plot_data(graph_type), sample_name, graph_type)
            graph.grid(column=0, row=0, columnspan=2, rowspan=1)
        else:
            for ind, graph_type in enumerate(GraphType):
                graph = self.generate_graph(analyzer.get_plot_data(graph_type), sample_name, graph_type)
                graph.grid(column=ind, row=0, columnspan=1, rowspan=1)

    def generate_graph(self, 
                       plot_data: PlotData, sample_name: str, graph_type: GraphType
                       ) -> tk.Canvas:
        '''
            Generates the graph/plot as a layout ready widget
            - -> ctk.CTkCanvas
        '''
        self.fig, self.ax = plt.subplots()
        self.fig.set_layout_engine('constrained')
        self.canvas = FigureCanvasTkAgg(self.fig, self) 
        graph_name = self.graph_names[graph_type]

        title: str = f"{graph_name}\n{sample_name}"

        self.x, self.y, self.points = plot_data
        Plotter(self.x, self.y, self.points, self.ax, graph_type)
                     
        self.ax.set_title(title)

        return self.canvas.get_tk_widget()


class DataPanal(ctk.CTkFrame):
    '''
        CTkFrame:
        Views the data and resulting stats
    '''
    def __init__(self, master: AnalysisPanal) -> None:
        super().__init__(master)

        self.note_font: ctk.CTkFont = ctk.CTkFont('JetBrainsMono', 14, 'bold')

        self.data_note: DataNote = DataNote(self, self.note_font) 
        self.stats_note: StatsNote = StatsNote(self, self.note_font)

        self.data_note.pack(side='left', fill='both', expand=1, padx=5, pady=5)
        self.stats_note.pack(side='left', fill='both', expand=1, padx=5, pady=5)

    def write(self, analyzer: Analyzer, sample: Sample, _type: GraphType):
        
        stats = analyzer.get_stats()
        #! The format doesn't show up correctly in the text panal (stats_note)
        stats_massage: str = "".join([f"\n{k.capitalize()}\t>  {v:.3f}" for k ,v in stats.items()])
        sample_data_massage: str = sample.get_data().to_string(index=False, col_space= 10, justify='center')
        self.data_note.update_note(sample_data_massage)
        self.stats_note.update_note(stats_massage)


class DataNote(ctk.CTkTextbox):

    def __init__(self, master: DataPanal, font: ctk.CTkFont) -> None:
        super().__init__(master)
        self.configure(state=ctk.DISABLED, font=font, tabs=150)  

    def update_note(self, text: str ) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert("1.0", text)
                self.configure(state=ctk.DISABLED)  


class StatsNote(ctk.CTkTextbox):

    def __init__(self, master: DataPanal, font: ctk.CTkFont) -> None:
        super().__init__(master)
        self.configure(state=ctk.DISABLED, font=font, tabs=150)    

    def update_note(self, text: pd.DataFrame|str ) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert("1.0", text)
                self.configure(state=ctk.DISABLED)  

        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 