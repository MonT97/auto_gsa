from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, Event
from enums import GraphType, FileFormat
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
        self.samples_file_viewer.bind("<<TreeviewSelect>>", 
                              lambda event: self.set_data(self.samples_file_viewer.selection(), GraphType.CUM, event))
        self.samples_file_viewer.event_add("<<QuickAnalysisCum>>", "<Alt-Button-1>")
        self.samples_file_viewer.event_add("<<QuickAnalysisHis>>", "<Shift-Button-1>")
        self.samples_file_viewer.bind("<<QuickAnalysisCum>>", 
                              lambda event: self.set_data(self.samples_file_viewer.selection(), GraphType.CUM, event))
        self.samples_file_viewer.bind("<<QuickAnalysisHis>>", 
                              lambda event: self.set_data(self.samples_file_viewer.selection(), GraphType.HIST, event))

        self.analyze_btn: ctk.CTkButton = ctk.CTkButton(self,
            text="analyze",
            state="disabled",
            command=lambda: self.analyze(self.data, GraphType.CUM))
        self.save_all_btn: ctk.CTkButton = ctk.CTkButton(self,
                                                        text="save all",
                                                        state="disabled",
                                                        command=lambda: self.save_all())
        self.save_btn: ctk.CTkButton = ctk.CTkButton(self,
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

    def set_data(self, selection: tuple, _type: GraphType, event: Event=None): # type: ignore
        
        self.analyze_btn.configure(state="normal")
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
            cum_points, hist_points = [Analyzer(sample.get_data(), i).get_plot_data() for i in GraphType]
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

        for index, file_ in enumerate(os.listdir(_dir)):
            if file_.split(".")[-1] in self.formats:
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
            - display the sample name [sample_name_label: ctk.CTkLabel].
            - display the sample data and the analysis result [analysis_book: AnalysisBook]
    '''
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        self.sample_name_label: ctk.CTkLabel = ctk.CTkLabel(
            self, text="\nSample Name", anchor="center")
        self.analysis_book: AnalysisBook = AnalysisBook(self)

        self.sample_name_label.pack(fill="x", ipady=5, padx=5, pady=5)
        self.analysis_book.pack(expand=1, fill="both", padx=5, pady=5)
        self.result_dir: str = ""

    def write(self, sample: Sample, _type: GraphType):

        self.sample_name_label.configure(text=sample.get_name())
        self.analysis_book.write(sample, _type)
        self.analysis_book.draw_graph(sample, _type)
    
    def save_data(self, sample: Sample, sample_dir: str, itr: str | int = "", t = None):

        #! check for a better way to do it, and make it consistant between runs!
        if not self.result_dir:
            self.result_dir = os.path.join(sample_dir, "results")
        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)
        if not t:
            with pd.ExcelWriter(os.path.join(self.result_dir, f"{sample.get_name()}.xlsx"),
                        engine='openpyxl',
                        mode='w') as writer:
                sample.get_data().to_excel(writer, index=False)
            self.analysis_book.graph_tab.fig.savefig(
            os.path.join(self.result_dir, f"{sample.get_name()}.svg"), format="svg")
        if t:
            t.savefig(os.path.join(self.result_dir, f"all_samples_{itr}.svg"), format="svg")
        


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

        self.stats = Analyzer(sample.get_data(), _type).get_stats()
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

        #TODO let the plotter produce both graphs then let the choice be done via this button!
        self.graph_toggle_txt: ctk.StringVar = ctk.StringVar(self, value='graph')
        self.graph_toggle: ctk.CTkButton = ctk.CTkButton(
            self, text=self.graph_toggle_txt.get(),
            textvariable=self.graph_toggle_txt)
        self.graph_toggle.place(anchor='ne', relx=.975, rely=.025)

    def draw_graph(self, sample: Sample, graph_type: GraphType) -> None:

        self.graph_name = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}

        self.sample_name: str = sample.get_name()
        self.sample_data: pd.DataFrame = sample.get_data()

        self.ax.cla()

        self.title: str = f"{self.graph_name[graph_type]}\n{self.sample_name}"

        self.x, self.y, self.points = Analyzer(self.sample_data, graph_type).get_plot_data()
        Plotter(self.x, self.y, self.points, self.ax, graph_type)
        self.graph_toggle_txt.set(value=f"{self.graph_name[graph_type].split(" ")[0]}")
                     
        self.ax.set_title(self.title)
        self.canvas.figure = self.fig
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=1, fill="both", padx=5, pady=5)
        
        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 