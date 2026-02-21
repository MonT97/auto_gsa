import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typedefs import GraphType, FileFormat, PlotData, SampleStats, StatsInterpretation
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
        self.sample: Sample = Sample()
        self.data: tuple = ()

        self.supported_formats: list[str] = [_format.value for _format in FileFormat]

        self.entry = ctk.CTkEntry(self, placeholder_text="Enter the samples folder path...")
        self.entry.bind("<KeyPress-Return>", command= lambda _: self._import_files())
        self.entry.bind('<Enter>', lambda _: self.entry.focus_set())
        self.entry.bind('<KeyPress-Escape>', lambda _: self._reset_focus())
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

    def _create_analyzer(self, sample: Sample) -> None:
        if self.current_sample != sample:
            self.analyzer: Analyzer = Analyzer(sample.get_data())

    def draw_graphs(self, sample: Sample, graph_type: GraphType|None) -> None:
        self._create_analyzer(sample)
        #? is this the best place for this? NO, actually it might
        self.graph_panal.draw_graphs(self.analyzer, sample.get_name(), graph_type)      

    def write(self, sample: Sample, graph_type: GraphType) -> None:
        self._create_analyzer(sample)
        self.data_panal.write(self.analyzer, sample, graph_type)


class GraphPanal(ctk.CTkFrame):
    '''
    CTkFrame:
    View the resulting graphs
    '''
    #TODO add the ability to change the graph color, maybe only during saves as this is a preview!?
    def __init__(self, master: AnalysisPanal) -> None:
        super().__init__(master)

        self.graph_color: str = '#1f7bb4'
        self.graphs: list[Axes] = []
        self.graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}

        self.graph_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.graph_frame.columnconfigure(0, weight=1, uniform='a')
        self.graph_frame.columnconfigure(1, weight=1, uniform='a')
        self.graph_frame.rowconfigure(0, weight=1, uniform='a')

        self.graph_frame.pack(fill='both', expand=1, padx=5, pady=5)

        self.cust_bar: CustomizationBar = CustomizationBar(self, .3, .28)

    def _generate_graph(self, 
                       plot_data: PlotData, sample_name: str, graph_type: GraphType,
                       color: str
                       ) -> tk.Canvas:
        '''
        Generates the graph/plot as a layout ready widget
        - -> ctk.CTkCanvas
        '''
        fig, ax = plt.subplots()
        fig.set_layout_engine('constrained')
        canvas = FigureCanvasTkAgg(fig, self.graph_frame) 
        graph_name = self.graph_names[graph_type]

        title: str = f"{graph_name}\n{sample_name}"

        self.x, self.y, self.points = plot_data
        Plotter(self.x, self.y, self.points, ax, graph_type, color)
                     
        ax.set_title(title)
        plt.close()
        return canvas.get_tk_widget()

    def draw_graphs(self,
                    analyzer: Analyzer, sample_name: str,
                    graph_type: GraphType|None, graph_color:str = '#1f7bb4') -> None:
        '''
        Layout the graphs
        - graph_type = None -> layout all the graphs in enums.GraphType
        '''
        #? resetting the layout!
        for i in self.graph_frame.grid_slaves():
            i.grid_forget()

        if graph_type:
            graph = self._generate_graph(analyzer.get_plot_data(graph_type), sample_name, graph_type, graph_color)
            graph.grid(column=0, row=0, columnspan=2, rowspan=1)
        else:
            for ind, _type in enumerate(GraphType):
                graph = self._generate_graph(analyzer.get_plot_data(_type), sample_name, _type, graph_color)
                graph.grid(column=ind, row=0, columnspan=1, rowspan=1)
        
        #! Rework the architecture to GraphPanal <--- cust_bar ---> clr_pickr
        self.cust_bar.set_graph_params(self.draw_graphs, analyzer, sample_name, graph_type)


class DataPanal(ctk.CTkFrame):
    '''
    CTkFrame:
    Views the data and resulting stats
    '''
    def __init__(self, master: AnalysisPanal) -> None:
        super().__init__(master)

        self.note_font: ctk.CTkFont = ctk.CTkFont('Arial', 14, 'bold')

        self.data_note: DataNote = DataNote(self, self.note_font) 
        self.stats_note: StatsNote = StatsNote(self, self.note_font)

        self.data_note.pack(side='left', fill='both', expand=1, padx=5, pady=5)
        self.stats_note.pack(side='left', fill='both', expand=1, padx=5, pady=5)

    def write(self, analyzer: Analyzer, sample: Sample, _type: GraphType):
        
        stats = analyzer.get_stats()
        interpretation = analyzer.get_interpretation()
        
        def _get_msg(inp) -> str:
            
            msg: str = ''
            inp_type = type(inp)

            if inp_type is SampleStats:
                msg = "".join([f"{k.capitalize()}\t> {v:.3f}\n" for k,v in inp.to_dict().items()])
            elif inp_type is StatsInterpretation:
                msg = "".join(
                    [f"{k.capitalize()}\t> {v.capitalize()}\n" for k,v in inp.to_dict().items()])
            elif inp_type is Sample:
                msg = inp.get_data().to_string(index=False, col_space= 10, justify='center')
            
            return msg
        
        sample_data_msg: str = _get_msg(sample)
        stats_msg: str = _get_msg(stats)
        interp_msg: str = _get_msg(interpretation)

        self.data_note.update_note(sample_data_msg)
        self.stats_note.update_note(stats_msg, interp_msg)

#TODO make it a table, TreeView, parent with file picker??, maybe not, as we don't need to select here!
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
        self.configure(state=ctk.DISABLED, font=font, tabs=95)    

    def update_note(self, stats: str, interpretation: str ) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert(self.index(tk.INSERT), "-Stats:\n")
                self.insert(self.index(tk.INSERT), stats)
                self.insert(self.index(tk.INSERT), "\n")
                self.insert(self.index(tk.INSERT), "-Interpretation:\n")
                self.insert(self.index(tk.INSERT), interpretation)
                self.configure(state=ctk.DISABLED)  


class CustomizationBar(ctk.CTkFrame):
    '''
    Gives the ability to change the graph preview visuals.
    '''
    def __init__(self, master:GraphPanal,
                 width: float, height:float, anim_speed: float =.01) -> None:
        super().__init__(master)

        #TODO: 2 row 1 col frame later for move_btn and the prior for the clr_pikr [as a frame]
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=4)
        # self.rowconfigure(1, weight=1)

        #TODO: move mv_btn here, and it mvmnt related functionality.

        #TODO: This handels the graph updating.

        offset: float = 0

        self.anim_speed: float = anim_speed

        self.width = width
        self.height = height

        self.initial_pos = .07
        self.crnt_y_pos = self.initial_pos
        self.final_pos = self.height + offset

        self.in_start_pos:bool = True

        self.clr_pikr: ColorPicker = ColorPicker(self)
        self.clr_pikr.pack(expand=1, fill='both')
        self.move_btn: ctk.CTkButton = self.clr_pikr.move_btn
        self.move_btn_txt: str = self.move_btn.cget('text')

        self._deligate_animation_function()

        self.place(anchor='s',
                relx=.5, rely=self.crnt_y_pos, relheight=self.height, relwidth=self.width)

    def animate(self):

        def _move():
            self.place(anchor='s',
                relx=.5, rely=self.crnt_y_pos, relheight=self.height, relwidth=self.width)
            self.after(10, self.animate) 

        if self.in_start_pos:
            if self.crnt_y_pos < self.final_pos:
                self.crnt_y_pos += self.anim_speed
                _move()
                return
            self.move_btn.configure(text= f'/ {self.move_btn_txt} \\')
            self.in_start_pos = not self.in_start_pos
        else:
            if self.crnt_y_pos > self.initial_pos:
                self.crnt_y_pos -= self.anim_speed
                _move()
                return
            self.move_btn.configure(text= f'\\ {self.move_btn_txt} /')
            self.in_start_pos = not self.in_start_pos
    
    def _deligate_animation_function(self) -> None:
        self.clr_pikr.set_animate_func(self.animate)

    def set_graph_params(self,
                         func, analyzer: Analyzer, sample_name: str,
                         graph_type: GraphType|None) -> None:
        
        self.clr_pikr.set_graph_params(func, analyzer, sample_name, graph_type)


class ColorPicker(ctk.CTkFrame):
    '''
    An (RGB) color picker.
    '''
    def __init__(self, master: CustomizationBar) -> None:
        super().__init__(master)

        #! admittedly a weak architectural choice, look for a better option!

        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=2, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')

        self.clr_frame = ctk.CTkFrame(self)
        self.clr_frame.columnconfigure(0, weight=1, uniform='b')
        self.clr_frame.columnconfigure(1, weight=2, uniform='b')
        self.clr_frame.rowconfigure(0, weight=1, uniform='b')
        self.clr_frame.rowconfigure(1, weight=1, uniform='b')
        self.clr_frame.rowconfigure(2, weight=1, uniform='b')

        self.color: str = '#000000'

        self.preview = ctk.CTkButton(self.clr_frame,
                                     text='set', border_color='red', border_width=2,
                                     command= lambda: self.update_graph())

        r: ctk.IntVar = ctk.IntVar(self, value=138)
        g: ctk.IntVar = ctk.IntVar(self, value=117)
        b: ctk.IntVar = ctk.IntVar(self, value=216)

        self._set_color((r,g,b))

        self.move_btn: ctk.CTkButton = ctk.CTkButton(self, corner_radius=0,
                text='\\ configuration /', state=ctk.DISABLED, height=100,
                command=lambda: self.move())

        r_slider: ctk.CTkSlider = ctk.CTkSlider(self.clr_frame,
                height=13, button_corner_radius=5, border_width=5, button_length=18,
                button_color='#b50000', button_hover_color='#ff0000', progress_color='#855656',
                from_=0, to=255, number_of_steps=255, variable=r,
                command=lambda _: self._set_color((r,g,b)))
        g_slider: ctk.CTkSlider = ctk.CTkSlider(self.clr_frame,
                height=13, button_corner_radius=5, border_width=5, button_length=18,
                button_color='#00b500', button_hover_color='#00ff00', progress_color='#568556',
                from_=0, to=255, number_of_steps=255, variable=g,
                command=lambda _: self._set_color((r,g,b)))
        b_slider: ctk.CTkSlider = ctk.CTkSlider(self.clr_frame,
                height=13, button_corner_radius=5, border_width=5, button_length=18,
                button_color='#0000b5', button_hover_color='#0000ff', progress_color='#565685',
                from_=0, to=255, number_of_steps=255, variable=b,
                command=lambda _: self._set_color((r,g,b)))
    
        self.preview.grid(column=0, row=0, rowspan=3, padx=5, pady=2, sticky='nsew')
        r_slider.grid(column=1, row=0, rowspan=1, padx=5)
        g_slider.grid(column=1, row=1, rowspan=1, padx=5)
        b_slider.grid(column=1, row=2, rowspan=1, padx=5)

        self.clr_frame.grid(column=0, row=0, sticky='nsew')
        self.move_btn.grid(column=0, row=1, sticky='nsew')

    def _set_color(self, rgb: tuple[ctk.IntVar,ctk.IntVar,ctk.IntVar]) -> None:
        '''
        Sets the color.
        '''
        clr = tuple(i.get() for i in rgb)
        
        self.color = f'#{clr[0]:02x}{clr[1]:02x}{clr[2]:02x}'
        self.preview.configure(fg_color = self.color)

        if sum(clr) > 245:
            self.preview.configure(text_color = '#000000')
        if sum(clr) < 245:
            self.preview.configure(text_color = '#ffffff')

        if self.preview.cget('border_color') != 'red':
            self.preview.configure(border_color='red', text='set')

    def set_graph_params(self,
                         func, analyzer: Analyzer, sample_name: str,
                         graph_type: GraphType|None) -> None:
        '''
        This represents the connection to the extra widget graphing function.
        '''
        self.widget_graph_func = func
        self.analyzer = analyzer
        self.sample_name = sample_name
        self.graph_type = graph_type
        self.move_btn.configure(state=ctk.NORMAL)

    def set_animate_func(self, animate_func) -> None:
        '''
        This represents the connection to the extra widget animation function.
        '''
        self.animate_func = animate_func

    def update_graph(self) -> None:
        '''
        Update the graph with the new color
        '''
        self.widget_graph_func(self.analyzer, self.sample_name, self.graph_type, self.color)
        self.preview.configure(border_color='green', text='set!')
    
    def move(self) -> None:
        '''
        Animate.
        '''
        self.animate_func()

        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 