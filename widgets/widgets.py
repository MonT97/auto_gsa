from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, Event
from enums import GraphType
from helpers import Analyzer, Plotter
from models import Sample

import customtkinter as ctk
import matplotlib.pyplot as plt
import pandas as pd
import os

class FilePanal(ctk.CTkFrame):
    '''
        CTkFrame:
        The class handeling:
            - picking the samples path [enery].
            - picking a sample [file_viewer].
            - Analyzing said sample [analyze_btn].
            - Saving said analysis resutls [save_btn].
    '''
    def __init__(self, master: ctk.CTk, analysis_panal):
        super().__init__(master)

        self.analysis_panal = analysis_panal
        self.samples_files_dir: str = ""
        self.sample: Sample = None # type: ignore
        self.data: tuple = ()

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter the sample folder")
        self.entry.bind("<KeyPress-Return>", command= lambda _event: self.import_files())
        self.file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import files",
            command=lambda: self.import_files())

        self.samples_file_viewer: FileViewer = FileViewer(self)
        self.samples_file_viewer.bind("<<TreeviewSelect>>", 
                              lambda event: self.set_data(self.samples_file_viewer.selection(), GraphType.CUM, event))
        self.samples_file_viewer.event_add("<<QuickAnalysisCum>>", "<Alt-Button-1>")
        self.samples_file_viewer.event_add("<<QuickAnalysisHis>>", "<Shift-Button-1>")
        self.samples_file_viewer.bind("<<QuickAnalysisCum>>", 
                              lambda event: self.set_data(self.samples_file_viewer.selection(), GraphType.CUM, event))
        self.samples_file_viewer.bind("<<QuickAnalysisHis>>", 
                              lambda event: self.set_data(self.samples_file_viewer.selection(), GraphType.HIST, event))

        self.analys_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analys",
            command=lambda: self.analyze(self.data, GraphType.CUM))
        self.save_btn: ctk.CTkButton = ctk.CTkButton(self,
                                                    text="save results",
                                                    state="disabled",
                                                    command=lambda: self.save_results(self.sample))

        self.entry.pack(side="top", fill="x", padx=5, pady=5)
        self.file_import_btn.pack(side="top", fill="x", padx=5, pady=5)
        self.samples_file_viewer.pack(side="top", padx=5)
        self.save_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        self.analys_btn.pack(side="bottom", fill="x", padx=5, pady=5)

    def import_files(self):

        self.samples_files_dir: str = self.entry.get()
        self.samples_file_viewer.display_files(self.samples_files_dir)

    def set_data(self, selection: tuple, _type: GraphType, event: Event=None): # type: ignore

        self.data = selection
        
        if event.state:
            self.analyze(self.data, _type)
        

    def analyze(self, table_selection: tuple, _type:GraphType):

        _type = _type
        sample_file_name = self.samples_file_viewer.get_data(table_selection)[-1]
        sample_data = pd.read_excel(f"{self.samples_files_dir}\\{sample_file_name}")

        self.sample: Sample = Sample(sample_file_name, sample_data) # type: ignore

        self.analysis_panal.write(self.sample, _type)
        self.save_btn.configure(state="normal")
    
    def save_results(self, sample: Sample):
        
        self.analysis_panal.save_data(sample, self.samples_files_dir)


class FileViewer(ttk.Treeview):
    '''
        Treeview:
        The class that views and give the ability to select samples.
        - display_files(dir: str) writes in the samples id and file_name.
        - get_data(selection_id: str) -> [id: int, sample_file_name: str].
    '''
    def __init__(self, master: FilePanal):
        super().__init__(master)

        self.configure(selectmode="browse",
                       show="headings",
                       columns = ["no", "file_name"])

        self.heading("no", text="NO", anchor="w")
        self.heading("file_name", text="File Name", anchor="w")

    def display_files(self, _dir: str) -> None:
        
        if self.get_children():
            [self.delete(i) for i in self.get_children()] 
        for index, file_ in enumerate(os.listdir(_dir)):
            if len(file_.split(".")) > 1:
                self.insert("", "end", values=[index, file_])

    def get_data(self, selection_id: tuple[int, None]) -> list[int|str]:

        self.item(selection_id[0])
        return self.item(selection_id)["values"] # type: ignore


class AnalysisPanal(ctk.CTkFrame):
    '''
        CTkFrame:
        The class that handels viewing and analyzing the data.
            - display the sample name [sample_name_label: ctk.CTkLabel].
            - display the sample data and the analysis result [analysis_book: AnalysisBook]
    '''
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        self.sample_name_label: ctk.CTkLabel = ctk.CTkLabel(self,
                                                            anchor="center",
                                                            text="Sample Name:")
        self.analysis_book: AnalysisBook = AnalysisBook(self)

        self.sample_name_label.pack(fill="x", padx=5, ipady=10)
        self.analysis_book.pack(expand=1, fill="both")
        self.result_dir: str = ""

    def write(self, sample: Sample, _type: GraphType):

        self.sample_name_label.configure(text=sample.get_name())
        self.analysis_book.write(sample, _type)
        self.analysis_book.draw_graph(sample, _type)
    
    def save_data(self, sample: Sample, sample_dir: str):

        #! check for a better way to do it, and make it consistant between runs!
        if not self.result_dir:
            self.result_dir = os.path.join(sample_dir, "results")
        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)
        with pd.ExcelWriter(os.path.join(self.result_dir, sample.get_name()),
                       engine='openpyxl',
                       mode='w') as writer:
            sample.get_data().to_excel(writer, index=False)
        self.analysis_book.graph_tab.fig.savefig(
            os.path.join(self.result_dir,
                         f"{sample.get_name()}.svg"),
            format="svg")


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

        self.data_tab: DataTab = DataTab(self.tab("data"))
        self.data_tab.pack_propagate(False)

        self.graph_tab: GraphTab = GraphTab(self.tab("graph"))
        self.graph_tab.pack_propagate(False)

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
        - display the data [note: CTkTextbox].
        - display the resulting stats [stats_note: CTkTextbox].
    '''
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master)

        self.note: ctk.CTkTextbox = ctk.CTkTextbox(self, state=ctk.DISABLED)
        self.stats_note: ctk.CTkTextbox = ctk.CTkTextbox(self, state=ctk.DISABLED)

        self.note.place(anchor="nw", relx=0, rely=0, relwidth=1, relheight=.5)
        self.stats_note.place(anchor="sw", relx=0, rely=1, relwidth=1, relheight=.5)        
    
    def write(self, sample: Sample, _type: GraphType):

        self.note.configure(state=ctk.NORMAL)
        self.note.delete("1.0", "end")
        self.note.insert("1.0", sample.get_data())
        self.note.configure(state=ctk.DISABLED)
        
        self.stats = Analyzer(sample.get_data(), _type).get_stats()
        self.stats_massage: str = "".join([f"\n{k.capitalize()} ---> {v}\n" for k ,v in self.stats.items()])
        
        self.stats_note.configure(state=ctk.NORMAL)
        self.stats_note.delete("1.0", "end")
        self.stats_note.insert("1.0", self.stats_massage)
        self.stats_note.configure(state=ctk.DISABLED)
    

class GraphTab(ctk.CTkFrame):
    '''
        The class that draw and view the data.
    '''
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master)

        # self.fig, self.axes = plt.subplots(1, 2) #? ?self.axes here is np[]
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(master=self)

    def draw_graph(self, sample: Sample, graph_type: GraphType) -> None:

        self.graph_name = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}

        self.sample_name: str = sample.get_name()
        self.sample_data: pd.DataFrame = sample.get_data()

        self.ax.cla()

        self.title: str = f"{self.sample_name}\n{self.graph_name[graph_type]}"

        self.x, self.y, self.points = Analyzer(self.sample_data, graph_type).get_plot_data()
        Plotter(self.x, self.y, self.points, self.ax, graph_type)
                     
        self.ax.set_title(self.title)
        self.canvas.figure = self.fig
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=1, fill="both", padx=5, pady=5)
        
        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 