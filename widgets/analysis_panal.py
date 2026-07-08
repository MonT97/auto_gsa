from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.axes import Axes
from typing import Callable

from typedefs import GraphType, PlotData, SampleStats, StatsInterpretation, AnalysisMethod, GraphParameters
from models import Sample, Analyzer, Cache
from shared_widgets import ColorPicker
from mixins import HasToolTip, CanPlot

import matplotlib.pyplot as plt
import customtkinter as ctk
import tkinter as tk

# Constants

# fonts:
DATA_NOTE_FONT = ('Arial', 14, 'bold')

# colors:
GRAPH_COLOR_DEFAULT = '#1f7bb4'

class AnalysisPanal(ctk.CTkFrame):
    """
    CTkFrame:
    The class that handels viewing and analyzing the data.
        - display the sample graphs [gaph_panal: ctk.CTkLabel].
        - display the sample data and the analysis result [data_panal: AnalysisBook]
    """
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master)

        self.configure(corner_radius=0)

        self.current_sample: Sample = Sample()

        self.graph_panal: GraphPanal = GraphPanal(self)
        self.data_panal: DataPanal = DataPanal(self)

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.rowconfigure(0, weight=5, uniform='a')
        self.rowconfigure(1, weight=4, uniform='a')

        self.graph_panal.grid(
            column=0, columnspan=2, row=0, rowspan=1,
            padx=5, pady=(5,0),sticky='nsew')
        self.data_panal.grid(
            column=0, columnspan=2, row=1, rowspan=1,
            padx=5, pady=5, sticky='nsew')

    def _create_analyzer(self, sample: Sample) -> None:
        if self.current_sample != sample:
            self.analyzer: Analyzer = Analyzer(sample.get_data())

    def draw_graphs(self, sample: Sample, graph_type: GraphType) -> None:
        """
        Triggered by an outside signal.
        """
        self._create_analyzer(sample)
        #? is this the best place for this? NO, actually it might
        self.graph_panal.draw_graphs(self.analyzer, sample.get_name(), graph_type, GRAPH_COLOR_DEFAULT)      

    def write(self, sample: Sample, graph_type: GraphType|None) -> None:
        """
        Triggered by an outside signal.
        """
        self._create_analyzer(sample)
        self.data_panal.write(self.analyzer, sample, graph_type)
    
    def get_graph_color(self) -> str:
        """
        Triggered by an outside signal.
        """
        return self.graph_panal.get_graph_params().graph_color


class GraphPanal(ctk.CTkFrame, CanPlot):
    """
    CTkFrame:
    Views the resulting graphs.
    """
    def __init__(self, master: AnalysisPanal) -> None:
        super().__init__(master)

        # Cache:
        self.graphs_cache: Cache = Cache(100)

        self.graphs: list[Axes] = []
        self.graph_color: str = GRAPH_COLOR_DEFAULT
        self.graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}

        self.graph_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.graph_frame.columnconfigure(0, weight=1, uniform='a')
        self.graph_frame.columnconfigure(1, weight=1, uniform='a')
        self.graph_frame.rowconfigure(0, weight=1, uniform='a')

        self.graph_frame.pack(fill='both', expand=1, padx=5, pady=5)

        self.cust_bar: CustomizationBar = CustomizationBar(self, .3, .25, .04)

    def _generate_graph(self, 
                       plot_data: PlotData, sample_name: str, graph_type: GraphType,
                       color: str) -> tk.Canvas:
        """
        Generates the graph/plot as a layout ready widget
        - -> tk.Canvas
        """
        _fig, _ax = plt.subplots()
        _fig.set_layout_engine('constrained')
        _canvas = FigureCanvasTkAgg(_fig, self.graph_frame) 
        _graph_name = self.graph_names[graph_type]

        _title: str = f"{_graph_name}\n{sample_name}"

        self.x, self.y, self.points, _analysis_method = plot_data
        self.cp_plot(self.x, self.y, self.points, _ax, graph_type, _analysis_method, color)
                     
        _ax.set_title(_title)
        plt.close()

        return _canvas.get_tk_widget()

    def _set_graph_params(self, analyzer: Analyzer, sample_name: str,
                          graph_type: GraphType, graph_color: str) -> None:
        """
        Saves the current params used to produce the graph as a praph_params dict.
        """
        self.graph_params: GraphParameters = GraphParameters()

        self.graph_params.analyzer = analyzer
        self.graph_params.graph_type = graph_type
        self.graph_params.sample_name = sample_name
        self.graph_params.graph_color = graph_color

    def get_graph_params(self) -> GraphParameters:
        """
        Returns the graph_params.
        """
        return self.graph_params

    def update_graphs(self, graph_params: GraphParameters) -> None:
        """
        Redraws the graph using the newly provided parameters.
        """
        _graph_params = graph_params.to_dict()
        self.draw_graphs(**_graph_params)
        self._set_graph_params(**_graph_params)

    def draw_graphs(self,
                    analyzer: Analyzer, sample_name: str,
                    graph_type: GraphType, graph_color:str) -> None:
        """
        Layout the graphs:
        - graph_type = None -> layout all the graphs in enums.GraphType.
        """
        _color_id = str(int(graph_color[1:],16))
        def get_canvas_obj(id_, type_) -> tk.Canvas:
            """
            Using the given [id_] and [type_], creates or retrives from cache then returns the tk.Canvas obj to plot.
            """
            _in_cache: Callable = lambda id_: self.graphs_cache.check(id_)
            if _in_cache(id_):
                _graph: tk.Canvas = self.graphs_cache.get(id_) #type: ignore
            else:
                _graph = self._generate_graph(analyzer.get_plot_data(type_), sample_name, type_, graph_color)
                self.graphs_cache.add(id_, _graph)
            
            return _graph

        # Resetting the layout:
        for i in self.graph_frame.grid_slaves():
            i.grid_forget()

        if graph_type:
            _id = sample_name+f'{graph_type}'+_color_id
            graph = get_canvas_obj(_id,graph_type) #type: ignore
            graph.grid(column=0, row=0, columnspan=2, rowspan=1) #type: ignore
        else:
            for ind, _type in enumerate(GraphType):
                _id = sample_name+f'{_type}'+_color_id
                graph = get_canvas_obj(_id,_type) #type: ignore
                graph.grid(column=ind, row=0, columnspan=1, rowspan=1) #type: ignore
        
        self._set_graph_params(analyzer, sample_name, graph_type, graph_color)
        self.cust_bar.enable()


class DataPanal(ctk.CTkFrame):
    """
    CTkFrame:
    Views the data and resulting stats
    """
    def __init__(self, master: AnalysisPanal) -> None:
        super().__init__(master)

        self.note_font: ctk.CTkFont = ctk.CTkFont(*DATA_NOTE_FONT)

        self.data_note: DataNote = DataNote(self, self.note_font) 
        self.stats_note: StatsNote = StatsNote(self, self.note_font)

        self.data_note.pack(side='left', fill='both', expand=1, padx=(5,0), pady=5)
        self.stats_note.pack(side='left', fill='both', expand=1, padx=5, pady=5)

    def write(self, analyzer: Analyzer, sample: Sample, _type: GraphType|None):
        
        _stats = analyzer.get_stats()
        _interpretation = analyzer.get_interpretation()
        
        def _get_msg(inp) -> str:
            
            _inp_type = type(inp)

            if _inp_type is SampleStats:
                _msg = "".join([f"{k.capitalize()}\t> {v:.3f}\n" for k,v in inp.to_dict().items()])
            elif _inp_type is StatsInterpretation:
                _msg = "".join(
                    [f"{k.capitalize()}\t> {v.capitalize()}\n" for k,v in inp.to_dict().items()]
                    )
            elif _inp_type is Sample:
                _msg = inp.get_data().to_string(index=False, col_space= 10, justify='center')
            else:
                _msg = ''
            
            return _msg
        
        _sample_data_msg: str = _get_msg(sample)
        _stats_msg: str = _get_msg(_stats)
        _interp_msg: str = _get_msg(_interpretation)
        _ana_method: AnalysisMethod = analyzer.get_method()
        
        self.data_note.update_note(_sample_data_msg)
        self.stats_note.update_note(_stats_msg, _interp_msg, _ana_method)

#TODO make it a table, TreeView, parent with file picker??, maybe not, as we don't need to select here!
class DataNote(ctk.CTkTextbox):
    """
    CTkTextbox
    """
    def __init__(self, master: DataPanal, font: ctk.CTkFont) -> None:
        super().__init__(master)
        self.configure(state=ctk.DISABLED, font=font, tabs=150)  

    def update_note(self, text: str ) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert("1.0", text)
                self.configure(state=ctk.DISABLED)  


class StatsNote(ctk.CTkTextbox):
    """
    CTkTextbox
    """
    def __init__(self, master: DataPanal, font: ctk.CTkFont) -> None:
        super().__init__(master)
        self.configure(state=ctk.DISABLED, font=font, tabs=95)    

    def update_note(self, stats: str, interpretation: str, analysis_method: AnalysisMethod) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete('1.0', ctk.END)
                self.insert(ctk.INSERT, "-Stats:\n")
                self.insert(ctk.INSERT, stats)
                self.insert(ctk.INSERT, "\n")
                self.insert(ctk.INSERT, "-Interpretation:\n")
                self.insert(ctk.INSERT, interpretation)
                self.insert(ctk.INSERT, "[Method Used]: ")
                self.insert(ctk.INSERT, analysis_method.value)
                self.configure(state=ctk.DISABLED)  


class CustomizationBar(ctk.CTkFrame, HasToolTip):
    """
    CkFrame:
        Gives the ability to change the graph preview visuals.
    """
    def __init__(self, master:GraphPanal,
                 width: float, height:float, anim_speed: float =.01) -> None:
        super().__init__(master)
        
        _offset: float = 0

        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=3, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')

        self.master: GraphPanal = master
        self.anim_speed: float = anim_speed

        self.width = width
        self.height = height

        self.initial_pos = .07
        self.crnt_y_pos = self.initial_pos
        self.final_pos = self.height + _offset

        self.in_start_pos:bool = True

        _clr_pikr: ColorPicker = ColorPicker(self)

        self.move_btn_txt: str = 'configuration'
        self.move_btn: ctk.CTkButton = ctk.CTkButton(self, corner_radius=0,
                height=100, text=f'\\ {self.move_btn_txt} /', state=ctk.DISABLED,
                command=lambda: self.animate())

        _clr_pikr.grid(column=0, row=0, sticky='nsew')
        self.move_btn.grid(column=0, row=1, sticky='nsew')

        self.place(anchor='s',
                relx=.5, rely=self.crnt_y_pos, relheight=self.height, relwidth=self.width)

    def _update_graphs(self, graph_params: GraphParameters) -> None:
        """
        Delegates the graph update process to master: GraphPanal
        """
        self.master.update_graphs(graph_params)

    def animate(self) -> None:
        """
        Animates self into place
        """
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
    
    def on_preview_press(self , color: str) -> None:
        """
        Triggerd by a preview button press From the clr_pikr: ColorPicker.
        """
        graph_params: GraphParameters = self.master.get_graph_params()
        graph_params.graph_color = color
        self._update_graphs(graph_params)
        self.winfo_toplevel().event_generate("<<AnalysisPanal-color>>")

    def enable(self) -> None:
        """
        Make interactable.
        """
        if self.move_btn.cget('state') == ctk.DISABLED:
            self.move_btn.configure(state=ctk.NORMAL)
            self.htt_tip(self.move_btn, 'click to edit the graphs, color, etc,...')

        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 