from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import CubicSpline
from tkinter import ttk, Event
from matplotlib.axes import Axes
from matplotlib import rc

import customtkinter as ctk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import shutil
import os

class FilePanal(ctk.CTkFrame):

    def __init__(self, master: ctk.CTk, analysis_book):
        super().__init__(master)

        self.analysis_book = analysis_book
        self.file_dir: str = ""
        self.data = None

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter the sample folder")
        self.entry.bind("<KeyPress-Return>", command= lambda _event: self.import_files())
        self.file_import_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="import files",
            command=lambda: self.import_files())

        self.file_viewer: FileViewer = FileViewer(self)
        #! add ability to ctr+click in the file_viewr to run the analysis self.analys()
        self.file_viewer.bind("<<TreeviewSelect>>",lambda event: self.set_data(self.file_viewer.selection(), event))
        self.file_viewer.event_add("<<QuickAnalysisCum>>", "<Control-Button-1>")
        self.file_viewer.event_add("<<QuickAnalysisHis>>", "<Shift-Button-1>")
        self.file_viewer.bind("<<QuickAnalysisCum>>", 
                              lambda event: self.set_data(self.file_viewer.selection(), event))
        self.file_viewer.bind("<<QuickAnalysisHis>>", 
                              lambda event: self.set_data(self.file_viewer.selection(), event))

        self.entry.pack(side="top", fill="x")
        self.file_import_btn.pack(side="top", fill="x", pady=5)
        self.file_viewer.pack(side="top", padx=5)

        self.save_cbox: ctk.CTkCheckBox = ctk.CTkCheckBox(self, text="save results")

        self.analys_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analys",
            command=lambda: self.analyze(self.data, "cum"))
        self.save_btn: ctk.CTkButton = ctk.CTkButton(self,
                                                    text="save results",
                                                    command=lambda: self.save_results())

        self.analys_btn.pack(side="bottom", fill="x")
        self.save_cbox.pack(side="bottom", pady=5)

    def import_files(self, event=None):

        self.file_dir: str = self.entry.get()
        self.file_viewer.display_files(self.file_dir)

    def set_data(self, selection, event:Event=None):

        self.data = selection

        if event.state:
            _type = "hist" if event.state == 9 else "cum"
            self.analyze(self.data, _type)

    def analyze(self, table_scelection, _type:str):
        
        _type = _type
        sample_file_name = self.file_viewer.get_data(table_scelection)[-1]
        sample_data = pd.read_excel(f"{self.file_dir}\\{sample_file_name}")

        sample: dict = {"name": sample_file_name, "data": sample_data}
        
        self.analysis_book.write(sample, _type)
    
    def save_results(self):
        print("safing results")


class FileViewer(ttk.Treeview):

    def __init__(self, master: FilePanal):
        super().__init__(master)

        self.configure(selectmode="browse",
                       show="headings",
                       columns = ["no", "file_name"])

        self.heading("no", text="NO", anchor="w")
        self.heading("file_name", text="File Name", anchor="w")


    def display_files(self, dir: str):

        for index, file_ in enumerate(os.listdir(dir)):
            self.insert("", "end", values=[index, file_])


    def get_data(self, selection_id):

        return self.item(selection_id)["values"]


class AnalysisPanal(ctk.CTkFrame):
    '''
        The class that handels viewing and analyzing the data
    '''
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        self.sample_name_label: ctk.CTkLabel = ctk.CTkLabel(self,
                                                            anchor="center",
                                                            text="Sample Name:")
        self.analysis_book: AnalysisBook = AnalysisBook(self)

        self.sample_name_label.pack(fill="x", padx=5, ipady=10)
        self.analysis_book.pack(expand=1, fill="both")

    def write(self, sample: dict, _type:str):

        self.sample_name_label.configure(text=sample["name"].capitalize())
        self.analysis_book.write(sample, _type)
        self.analysis_book.draw_graph(sample, _type)


class AnalysisBook(ctk.CTkTabview):
    '''
        The Tabview class
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
    
    def write(self, sample: dict, _type:str):

        self.data_tab.write(sample)
        self.draw_graph(sample, _type)
    
    def draw_graph(self, sample: dict, _type:str):
        
        self.graph_tab.draw_graph(sample, _type)


class DataTab(ctk.CTkFrame):
    '''
        Data Table view and analyze
    '''
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master)

        self.note: ctk.CTkTextbox = ctk.CTkTextbox(self, state=ctk.DISABLED)
        self.note.pack(expand=1, fill="both", padx=5, pady=5)
    
    def write(self, sample: dict):
        
        sample_data = sample['data']
        sample_data['wht%'] = (sample_data['wht']/sample_data['wht'].sum()).round(2)
        sample_data['cum.wht%'] = sample_data['wht'].cumsum()

        _, sample_data = sample.values()

        self.note.configure(state=ctk.NORMAL)
        self.note.delete("1.0", "end")
        self.note.insert("1.0", sample_data)
        self.note.configure(state=ctk.DISABLED)
    

class GraphTab(ctk.CTkFrame):
    '''
        Draw and graph the data
    '''
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master)

        self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(master=self)


    def draw_graph(self, sample:dict, graph_type:str ="cum"):

        graph_name = {"hist": "Histogram", "cum": "Cumulative Curve"}

        sample_name: str = sample['name'].split(".")[0].capitalize()
        sample_data: pd.DataFrame = sample['data']

        fig, ax = plt.subplots(1, 1)

        ax: Axes = ax

        title: str = f"{sample_name}\n{graph_name[graph_type]}"

        match graph_type:
            
            #? maybe make a Analyser(sample: dict, graph_type:str) .analyze() -> analysis_result: str.graph() -> graph: image. will make the match here simpler and streamline the process to add more!!

            case "cum":

                x = sample_data['phi'] ##? add the unicode for phi!
                y = sample_data['cum.wht%']

                interp = CubicSpline(x, y)
                x = np.linspace(x.min(), x.max(), 500)
                y = interp(x)

                ax.set_xlim(x.min(), 5)
                ax.set_ylim(y.min(), 100)

                phi_perc: list[int] = [5, 16, 50, 84, 95]
                points: list[tuple[float,float]] = [
                    (round(np.interp(phi,y,x), 2), phi) for phi in phi_perc]
            
                ax.plot(x,y)

                for point in points:

                    ax.plot([ax.get_xlim()[0], point[0], point[0]],
                            [point[1], point[1], ax.get_ylim()[0]], '--k')
                    ax.plot(point[0], point[1], '--.k')
                    ax.annotate(f"x={round(point[0],2)}, y={point[1]}%",
                                xy=(point[0]+.2, point[1]))

                x_label: str  = "phi (\u00D8)"
                y_label: str = "cumulative weight %"
            
            case "hist":

                x = sample_data['phi']
                y = sample_data['wht']

                ax.bar(x,y)

                x_label: str = "phi (\u00D8)"
                y_label:str  = "wht"                

        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        self.canvas.figure = fig
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=1, fill="both", padx=5, pady=5)
        
        #! add the analysis and the data results into the GUI
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!