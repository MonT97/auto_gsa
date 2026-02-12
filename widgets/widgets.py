from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, Event
from enums import GraphType, FileFormat
from helpers import Analyzer, Plotter
from matplotlib.axes import Axes
from models import Sample

import customtkinter as ctk
import matplotlib.pyplot as plt
import pandas as pd
import os

class FilePanal(ctk.CTkFrame):
    '''
        CTkFrame:
        The class handeling:
            - picking the samples path [entry].
            - picking a sample [file_viewer].
            - Analyzing said sample [analyze_btn].
            - Saving said analysis resutls [save_btn].
    '''
    def __init__(self, master: ctk.CTk, analysis_panal):
        super().__init__(master)

        self.analysis_panal = analysis_panal
        self.samples_files_dir: str = ""
        self.sample: Sample = None #type: ignore
        self.data: tuple = ()

        self.supported_formats: list[str] = [i.value for i in FileFormat]

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter the samples folder path...")
        self.entry.bind("<KeyPress-Return>", command= lambda _event: self.import_files())
        self.file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import files",
            command=lambda: self.import_files())

        self.samples_file_viewer: FileViewer = FileViewer(self)

        self.samples_file_viewer.bind(
            "<<TreeviewSelect>>", 
            lambda event: self.set_data(self.samples_file_viewer.selection(), event))
        self.samples_file_viewer.event_add("<<QuickAnalysisHis>>", "<Shift-Button-1>")
        self.samples_file_viewer.bind(
            "<<QuickAnalysisHis>>", 
            lambda event: self.set_data(self.samples_file_viewer.selection(), event))

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
        self.samples_file_viewer.pack(side="top", fill="x", padx=5)
        self.save_all_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.save_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.analyze_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        
    def import_files(self):

        self.samples_files_dir: str = self.entry.get()
        self.samples_file_viewer.display_files(self.samples_files_dir)
        self.save_all_btn.configure(state="normal")

    def set_data(self, selection: tuple, event: Event=None): # type: ignore
        
        self.analyze_btn.configure(state="normal")
        self.data = selection
        
        if event.state:
            for _type in GraphType:
                self.analyze(self.data, _type)

    def analyze(self, table_selection: tuple, _type:GraphType):

        sample_file_name = self.samples_file_viewer.get_data(table_selection)[-1]
        sample_data = pd.read_excel(f"{self.samples_files_dir}\\{sample_file_name}")

        self.sample: Sample = Sample(sample_file_name, sample_data) # type: ignore

        self.analysis_panal.write(self.sample, _type)
        self.analysis_panal.draw_graph(self.sample, _type)

        self.save_btn.configure(state="normal")
    
    def save_results(self, sample: Sample):
        
        self.analysis_panal.save_data(sample, self.samples_files_dir)

    def save_all(self):

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

        self.configure(selectmode="browse",
                       show="headings",
                       columns = ["no", "file_name"])
        
        self.column('no', width=30, minwidth=30, stretch=False, anchor="center")

        self.heading("no", text="NO", anchor="w")
        self.heading("file_name", text="File Name", anchor="w")

    def display_files(self, _dir: str) -> None:
        
        if self.get_children():
            [self.delete(i) for i in self.get_children()]

        #TODO: add format support
        supported: function = lambda _file: _file.split(".")[-1] in self.formats
        for index, file_ in enumerate(os.listdir(_dir)):
            if supported(file_):
                self.insert("", "end", values=[f'{index:02}', file_])
            else:
                #TODO: add an error logging capacity
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
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

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

    def draw_graph(self, sample: Sample, _type: GraphType):
        self.graph_panal.draw_graph(sample, _type)

    def write(self, sample: Sample, _type: GraphType):
        self.data_panal.write(sample, _type)


class GraphPanal(ctk.CTkFrame):
    '''
        CTkFrame:
        View the resulting graphs
    '''
    def __init__(self, master: AnalysisPanal):
        super().__init__(master)


        self.graphs: list[Axes] = []
        self.fig, self.ax = plt.subplots(1, 1)
        #TODO side by side plots
        # self.fig, self.ax = plt.subplots(1, 2)
        # self.ax = self.ax.flatten()
        self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(master=self)

    def draw_graph(self, sample: Sample, graph_type: GraphType) -> None:

        self.graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}
        self.graph_name = self.graph_names[graph_type]

        self.sample_name: str = sample.get_name()
        self.sample_data: pd.DataFrame = sample.get_data()

        self.ax.cla()

        self.title: str = f"{self.graph_name}\n{self.sample_name}"

        self.x, self.y, self.points = Analyzer(self.sample_data).get_plot_data(graph_type)
        Plotter(self.x, self.y, self.points, self.ax, graph_type)
                     
        self.ax.set_title(self.title)
        self.canvas.figure = self.fig
        self.canvas.draw()


class DataPanal(ctk.CTkFrame):
    '''
        CTkFrame:
        View the resulting graphs
    '''

    def __init__(self, master: AnalysisPanal):
        super().__init__(master)

        self.data_note: DataNote = DataNote(self) 
        self.stats_note: StatsNote = StatsNote(self)

        self.data_note.pack(side='left', fill='both', expand=1, padx=5, pady=5)
        self.stats_note.pack(side='left', fill='both', expand=1, padx=5, pady=5)

    def write(self, sample: Sample, _type: GraphType):
        
        stats = Analyzer(sample.get_data()).get_stats()
        #! The format doesn't show up correctly in the text panal (stats_note)
        stats_massage: str = "".join([f"\n{k.capitalize()+' ':-<15}> {v}\n" for k ,v in stats.items()])
        print(stats_massage)
        
        self.data_note.update_note(sample.get_data())
        self.stats_note.update_note(stats_massage)


class DataNote(ctk.CTkTextbox):

    def __init__(self, master: DataPanal):
        super().__init__(master)

        self.configure(state=ctk.DISABLED)  

    def update_note(self, text: pd.DataFrame|str ) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert("1.0", text)
                self.configure(state=ctk.DISABLED)  


class StatsNote(ctk.CTkTextbox):

    def __init__(self, master: DataPanal):
        super().__init__(master)
        self.configure(state=ctk.DISABLED)    

    def update_note(self, text: pd.DataFrame|str ) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert("1.0", text)
                self.configure(state=ctk.DISABLED)  


class AnalysisBook(ctk.CTkTabview):
    '''
        CTkTabview:
        The class that handel the viewing and analyzing the data.
            - display the data and the resulting stats [data_tab: DataTab].
            - display the graphs [graph_tab: GraphTab]
    '''
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master)

        self.add("data")
        self.add("graph")

        self.configure(fg_color="#2b2b2b")

        self.data_tab: DataTab = DataTab(self.tab("data"))

        self.graph_tab: GraphTab = GraphTab(self.tab("graph"))

        self.data_tab.pack(expand=1, fill="both")
        self.graph_tab.pack(expand=1, fill="both")
    
    def write(self, sample: Sample, _type: GraphType):

        self.data_tab.write(sample, _type)
        self.draw_graph(sample, _type)
    
    def draw_graph(self, sample: Sample, _type: GraphType):
        
        self.graph_tab.draw_graph(sample, _type)


class DataTab(ctk.CTkFrame):
    '''
        CTkFrame:
        The class that views the sample data and the resulting stats.
        - display the data [data_note: CTkTextbox].
        - display the resulting stats [stats_note: CTkTextbox].
    '''
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master)

        self.pack_propagate(True)
        self.data_note: ctk.CTkTextbox = ctk.CTkTextbox(self, state=ctk.DISABLED)
        self.stats_note: ctk.CTkTextbox = ctk.CTkTextbox(self, state=ctk.DISABLED)

        self.data_label:ctk.CTkLabel = ctk.CTkLabel(self, text='Data:', anchor="w", bg_color="#2b2b2b")
        self.stats_label:ctk.CTkLabel = ctk.CTkLabel(self, text='Statistics:', anchor="w", bg_color="#2b2b2b")

        self.data_label.place(anchor="n", relx=.5, rely=0, relwidth=1, relheight=.05)
        self.data_note.place(anchor="n", relx=.5, rely=.05, relwidth=1, relheight=.45)
        self.stats_label.place(anchor="n", relx=.5, rely=.5, relwidth=1, relheight=.05)
        self.stats_note.place(anchor="n", relx=.5, rely=.55, relwidth=1, relheight=.45)        
    
    def write(self, sample: Sample, _type: GraphType) -> None:

        def update_note(note: ctk.CTkTextbox, text: pd.DataFrame|str ) -> None:
            
            note.configure(state=ctk.NORMAL)
            note.delete("1.0", "end")
            note.insert("1.0", text)
            note.configure(state=ctk.DISABLED)
        
        update_note(self.data_note, sample.get_data())

        self.stats = Analyzer(sample.get_data()).get_stats()
        #! The format doesn't show up correctly in the text panal (stats_note)
        self.stats_massage: str = "".join([f"\n{k.capitalize()+' ':-<15}> {v}\n" for k ,v in self.stats.items()])
        print(self.stats_massage)
        
        update_note(self.stats_note, self.stats_massage)


class GraphTab(ctk.CTkFrame):
    '''
        The class that draw and view the data.
    '''
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master)

        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(master=self)

    def draw_graph(self, sample: Sample, graph_type: GraphType) -> None:

        self.graph_name = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}

        self.sample_name: str = sample.get_name()
        self.sample_data: pd.DataFrame = sample.get_data()

        self.ax.cla()

        self.title: str = f"{self.graph_name[graph_type]}\n{self.sample_name}"

        self.x, self.y, self.points = Analyzer(self.sample_data).get_plot_data(graph_type)
        Plotter(self.x, self.y, self.points, self.ax, graph_type)
                     
        self.ax.set_title(self.title)
        self.canvas.figure = self.fig
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=1, fill="both", padx=5, pady=5)
        
        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 