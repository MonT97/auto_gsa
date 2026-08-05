import tkinter as tk
from tkinter import ttk
from typing import Callable, Final, overload

import customtkinter as ctk
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from mixins import CanPlot, HasToolTip, Observer
from models import Analyzer, Cache, Sample
from shared_widgets import ColorPicker
from typedefs import (AnalysisMethod, GraphParameters, GraphType, PlotData,
                      SampleStats, SaveObject, Signal, StatsInterpretation)

# Constants:
# fonts
STATS_NOTE_FONT: Final[tuple[str, int, str]] = ('Arial', 14, 'bold')

# colors
GRAPH_COLOR_DEFAULT: Final[str] = '#1f7bb4'

# customization bar
CUST_BAR_PARAMS: Final[tuple[float, float, float]] =  (.3, .25, .04)


class AnalysisPanel(ctk.CTkFrame, Observer):
    """
    CTkFrame:
    The class that handles viewing and analyzing the data.
        - displays the sample graphs [graph_panel: ctk.CTkLabel].
        - displays the sample data and the analysis result [data_panel: AnalysisBook]
    """
    def __init__(self, master: ctk.CTkFrame) -> None:
        """
        CTkFrame:
        The class that handles viewing and analyzing the data.
            - display the sample graphs [graph_panel: ctk.CTkLabel].
            - display the sample data and the analysis result [data_panel: AnalysisBook]
        """
        super().__init__(master)

        self.configure(corner_radius=0)

        self._current_sample: Sample = Sample()
        self._analyzer: Analyzer = Analyzer()

        self._graph_panel: GraphPanel = GraphPanel(self)
        self._data_panel: DataPanel = DataPanel(self)

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.rowconfigure(0, weight=5, uniform='a')
        self.rowconfigure(1, weight=4, uniform='a')

        self._graph_panel.grid(
                column=0, columnspan=2, row=0, rowspan=1,
                padx=5, pady=(5,0),sticky='nsew')
        self._data_panel.grid(
                column=0, columnspan=2, row=1, rowspan=1,
                padx=5, pady=5, sticky='nsew')

    def _update_analyzer(self, sample: Sample) -> None:
        """
        Creates an Analyzer object for the given [sample].
        """
        if self._current_sample != sample:
            self._analyzer = Analyzer(sample.get_data())

    def analyze(self,
                sample: Sample,
                save_obj: SaveObject,
                graph_type: GraphType|None = None) -> None:
        """
        Analyze the given [sample], triggered by an outside signal from [MainPanel].
        """
        self._update_analyzer(sample)
        self._draw_graphs(sample, save_obj, graph_type)
        self._write(sample, graph_type)

    def _draw_graphs(self, sample: Sample, save_obj: SaveObject,
                     graph_type: GraphType|None) -> None:
        """
        Draws the graphs using it.
        """
        #? is this the best place for this? NO, actually it might
        self._graph_panel.draw_graphs(
            self._analyzer, sample.get_name(), save_obj.get('color'), graph_type)      

    def _write(self, sample: Sample, graph_type: GraphType|None) -> None:
        """
        Writes the data and it's analysis into the [DataPanel].
        """
        self._data_panel.write(self._analyzer, sample, graph_type)
    

class GraphPanel(ctk.CTkFrame, CanPlot, HasToolTip):
    """
    CTkFrame:
    Views the resulting graphs.
    """
    def __init__(self, master: AnalysisPanel, height: int = 200) -> None:
        """
        CTkFrame:
        Views the resulting graphs.
        """
        super().__init__(master, height=height)

        # Cache:
        self._graphs_cache: Cache = Cache()

        self._graph_params: GraphParameters = GraphParameters()
        self._graph_is_expanded: bool = False
        self._graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}

        self._graph_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self._graph_frame.columnconfigure(0, weight=1, uniform='a')
        self._graph_frame.columnconfigure(1, weight=1, uniform='a')
        self._graph_frame.rowconfigure(0, weight=1, uniform='a')

        self._label = ctk.CTkLabel(self, text='Graphs:', font=STATS_NOTE_FONT)
        
        self._label.pack(side='top', padx=5, anchor='w')
        self._graph_frame.pack(fill='both', expand=1, padx=5, pady=5)

        self.cust_bar = CustomizationBar(self, 
                        self._graph_params, self.update_graphs, *CUST_BAR_PARAMS)

    def _generate_graph(self, 
                       plot_data: PlotData, sample_name: str,
                       graph_type: GraphType, color: str) -> tk.Canvas:
        """
        Generates the graph/plot as a layout ready widget.
        """
        _fig, _ax = plt.subplots()
        _fig.set_layout_engine('constrained')
        _canvas = FigureCanvasTkAgg(_fig, self._graph_frame) 
        _graph_name = self._graph_names[graph_type]

        _title: str = f"{_graph_name}\n{sample_name}"

        self.cp_plot(*plot_data, _ax, graph_type, color)
                     
        _ax.set_title(_title)
        plt.close()

        return _canvas.get_tk_widget()

    def _set_graph_params(self, analyzer: Analyzer, sample_name: str,
                          graph_color: str, graph_type: GraphType|None = None) -> None:
        """
        Saves the current params used to produce the graph as a GraphParameters object.
        """
        self._graph_params.update(
                analyzer=analyzer, sample_name=sample_name,
                graph_type=graph_type, graph_color=graph_color)

    def update_graphs(self, graph_params: GraphParameters) -> None:
        """
        Redraws the graph using the newly provided parameters.
        """
        self.draw_graphs(**graph_params)
        self._set_graph_params(**graph_params)

    def draw_graphs(self,
                    analyzer: Analyzer, sample_name: str,
                    graph_color:str, graph_type: GraphType|None = None) -> None:
        """
        Layout the graphs:
        - `graph_type` = None -> layout all the graphs in enums.GraphType.
        """
        _color_id = str(int(graph_color[1:],16))
        _graphs_list: list[tk.Canvas] = []

        def _get_canvas_obj(id_, type_) -> tk.Canvas:
            """
            Using the given [id_] and [type_], creates or retrieves from cache then returns the tk.Canvas obj to plot.
            """
            _in_cache: bool = self._graphs_cache.check(id_)
            if _in_cache:
                _graph: tk.Canvas = self._graphs_cache.get(id_)
            else:
                _graph = self._generate_graph(analyzer.get_plot_data(type_), sample_name, type_, graph_color)
                self._graphs_cache.add(id_, _graph)

            _graphs_list.append(_graph)

            _graph.bind('<Button-1>', lambda _: self._expand_graph(_graph))
            _graph.bind('<Leave>', lambda _: self._revert_layout(_graphs_list))
            self.htt_tip(_graph, f'{self._graph_names[type_].lower()}\nclick to expand/shrink')

            return _graph

        # Resetting the layout:
        self._clear_layout()
        
        if graph_type:
            _id = sample_name+f'{graph_type}'+_color_id
            graph = _get_canvas_obj(_id,graph_type)
            graph.grid(column=0, row=0, columnspan=2, rowspan=1)
        else:
            for ind, _type in enumerate(GraphType):
                _id = sample_name+f'{_type}'+_color_id
                graph = _get_canvas_obj(_id,_type)
                graph.grid(column=ind, row=0, columnspan=1, rowspan=1)
                
        self._set_graph_params(analyzer, sample_name, graph_color ,graph_type)
        
        self.cust_bar.enable()

    def _expand_graph(self, graph: tk.Canvas) -> None:
        """
        Fills the grid layout with the provided [graph].
        """
        self._clear_layout()
        if not self._graph_is_expanded:
            graph.grid(column=0, row=0, columnspan=2, rowspan=1, sticky='nsew')
            self._graph_is_expanded = True

    def _revert_layout(self, graphs_list: list[tk.Canvas]) -> None:
        """
        Reverts to the typical layout.
        """
        self._clear_layout()
        for ind, graph in enumerate(graphs_list):
            graph.grid(column=ind, row=0, columnspan=1, rowspan=1)
        self._graph_is_expanded = False

    def _clear_layout(self) -> None:
        """
        Clears the layout.
        """
        for graph in self._graph_frame.grid_slaves():
            graph.grid_forget()


class DataPanel(ctk.CTkFrame):
    """
    CTkFrame:
    Views the data and resulting stats
    """
    def __init__(self, master: AnalysisPanel, height: int = 200) -> None:
        super().__init__(master, height=height)
        self._label = ctk.CTkLabel(self,
                text='Data and analysis:', font=STATS_NOTE_FONT)

        # housing frame:
        self.table_note_frame = ctk.CTkFrame(self)
        self.table_note_frame.columnconfigure(0, weight=1, uniform='a')
        self.table_note_frame.columnconfigure(1, weight=1, uniform='a')
        self.table_note_frame.rowconfigure(0, weight=1, uniform='a')

        self.stats_note_font: ctk.CTkFont = ctk.CTkFont(*STATS_NOTE_FONT)

        self.data_table = DataTable(self.table_note_frame)
        self.stats_note = StatsNote(self.table_note_frame, self.stats_note_font)

        # layout:
        self.data_table.grid(column=0, row=0, sticky='nsew', padx=(5,0), pady=(5,5))
        self.stats_note.grid(column=1, row=0, sticky='nsew', padx=5, pady=(5,5))
        
        self._label.pack(side='top', padx=5, anchor='w')
        self.table_note_frame.pack(side='top', fill='both', expand=1, padx=5, pady=(0,5))

    def write(self, analyzer: Analyzer, sample: Sample, _type: GraphType|None):
        """
        Extracts data form [analyzer] and [sample] then writes it into the [self.data_table] and the [self.stats_note].
        """
        _stats: SampleStats = analyzer.get_stats()
        _interpretation: StatsInterpretation = analyzer.get_interpretation()
        _ana_method: AnalysisMethod = analyzer.get_method()        

        @overload
        def _get_msg(inp: Sample) -> pd.DataFrame:...
        @overload
        def _get_msg(inp: SampleStats) -> str:...
        @overload
        def _get_msg(inp: StatsInterpretation) -> str:...
        def _get_msg(inp: Sample|SampleStats|StatsInterpretation) -> str|pd.DataFrame:
            if isinstance(inp, SampleStats):
                _msg = "".join([f"{k.capitalize()}\t> {v:.3f}\n" for k,v in inp.to_dict().items()])
            elif isinstance(inp, StatsInterpretation):
                _msg = "".join(
                    [f"{k.capitalize()}\t> {v.capitalize()}\n" for k,v in inp.to_dict().items()]
                    )
            elif isinstance(inp, Sample):
                _msg = inp.get_data()
                
            return _msg
        
        _sample_msg: pd.DataFrame = _get_msg(sample)
        _stats_msg: str = _get_msg(_stats)
        _interp_msg: str = _get_msg(_interpretation)
        
        self.data_table.populate_table(_sample_msg)
        self.stats_note.update_note(_stats_msg, _interp_msg, _ana_method)


class DataTable(ttk.Treeview, HasToolTip):
    """
    ttk.TreeView.
    """
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master)

        # Fonts and colors are set using the theme module.
        self.width: int = 0
        self.pad_value: int = 4 #subtracted from other cols to account for the bigger last one.
        self.col_width: int = 0

        self.activate_tip: bool = False
        #TODO: mm scale?!, Analyzer is the starting point for this
        self.hdr_tip_dict: dict[str,str] = {}
        self.hdr_names: list[str] = ['sieve size in phi scale',
                                     'retained weight fraction in grams',
                                     'weight fraction as percent of the total',
                                     'cumulative weight fractions as percents']

        self.bind("<Map>", lambda _: _set_element_width(self.winfo_width()))
        self.bind("<Motion>", lambda event: self._on_mouse_motion(event))
        self.bind("<Leave>", lambda _: self._on_mouse_exited())

        def _set_element_width(width: int) -> None:
            """
            Programmatically set the size of each TreeView column.
            """
            self.width = width
            width -= width%2
            self.col_width = (width//4)-self.pad_value

        self.configure(style='DataTable.Treeview', selectmode="none", show="headings")

    def _on_mouse_motion(self, event: tk.Event) -> None:
        """
        To manage to the initialization of the tooltip.
        """
        _pos: tuple[int,int] = (event.x, event.y)
        _area: str = self.identify_region(*_pos)
        if _area == 'heading':
            _col_id = self.identify_column(_pos[0])
            _hdr_name = self.heading(_col_id)['text']
            if not self.activate_tip:
                self.tip = self.htt_tip(self, self.hdr_tip_dict[_hdr_name], id_=_hdr_name)
                self.tip.on_enter(event)
                self.activate_tip = True
        else:
            self._on_mouse_exited()

    def _on_mouse_exited(self) -> None:
        """
        To disable the tooltip.
        """
        if self.activate_tip:
            self.tip.destroy()
            self.activate_tip = False

    def populate_table(self, data: pd.DataFrame) -> None:
        """
        Fills the table.
        - `data`: used to populate the table.
        """    
        _header: list[str] = data.columns.to_list()
        self.hdr_tip_dict = {k: v for k,v in zip(_header, self.hdr_names)}
        _last_col_width = self.width - (self.col_width*(len(_header)-1))

        _n_rows = data.shape[0]-1 # as the first row is the header
        _rows = [data.iloc[i+1,:].to_list() for i in range(_n_rows)]
        
        self.configure(columns=_header)

        # clear entries:
        if self.get_children():
            for file_name in self.get_children():
                self.delete(file_name)

        # handle headers:
        for hdr in _header:
            _width = self.col_width
            self.heading(hdr, text=hdr, anchor="center")
            if _header.index(hdr) == len(_header)-1:
                # this 21 is trail&error driven, as the last column name is typically longer. 
                _width = _last_col_width
            self.column(hdr, width=_width,
                    minwidth=_width, stretch=True, anchor="center")
        
        # handle data:
        for ind, ele in enumerate(_rows):
            if (ind%2 != 0):
                self.insert("", "end", values=ele, tags='odd')
                continue
            self.insert("", "end", values=ele)
        
        self.tag_configure('odd', background='#2b2b2b')
        
class StatsNote(ctk.CTkTextbox):
    """
    CTkTextbox
    """
    def __init__(self, master: ctk.CTkFrame, font: ctk.CTkFont) -> None:
        super().__init__(master)
        self.configure(state=ctk.DISABLED, font=font, tabs=95)    

    def update_note(self, stats: str, interpretation: str, analysis_method: AnalysisMethod) -> None:
                
        self.configure(state=ctk.NORMAL)
        self.delete('0.0', ctk.END)
        self.insert(ctk.INSERT, '-Stats:\n')
        self.insert(ctk.INSERT, stats)
        self.insert(ctk.INSERT, '\n')
        self.insert(ctk.INSERT, '-Interpretation:\n')
        self.insert(ctk.INSERT, interpretation)
        self.insert(ctk.INSERT, '[Method Used]: ')
        self.insert(ctk.INSERT, analysis_method.value)
        self.configure(state=ctk.DISABLED)  

#! Contemplate ConnectioObject!
class CustomizationBar(ctk.CTkFrame, HasToolTip, Observer):
    """
    CkFrame:
        Gives the ability to change the graph preview visuals.
    """
    def __init__(self, master:GraphPanel,
                 graph_params: GraphParameters, connection_func: Callable,
                 width: float, height:float, anim_speed: float =.01) -> None:
        """
        CkFrame:
            Gives the ability to change the graph preview visuals.
        """
        super().__init__(master)
        
        _offset: float = 0

        self.master: GraphPanel = master
        self._con_func = connection_func
        self._graph_parms = graph_params

        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=3, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')

        # animation:
        self.width = width
        self.height = height

        self.init_y_pos : float = .07
        self.crnt_y_pos = self.init_y_pos
        self.final_pos = self.height + _offset

        self.in_start_pos:bool = True

        self.clr_pikr: ColorPicker = ColorPicker(self)
        self.obs_listen(Signal.COLOR, self, self.on_color_picked)
        
        self.move_btn_txt: str = 'edit'
        self.move_btn: ctk.CTkButton = ctk.CTkButton(self, corner_radius=0,
                height=100, text=f'\\ {self.move_btn_txt} /', state=ctk.DISABLED,
                command=lambda: self.animate(anim_speed))

        # Layout:
        self.clr_pikr.grid(column=0, row=0, sticky='nsew')
        self.move_btn.grid(column=0, row=1, sticky='nsew')

        self.place(anchor='s',
                relx=.5, rely=self.crnt_y_pos, relheight=self.height, relwidth=self.width)

    def animate(self, animation_speed: float) -> None:
        """
        Animates self into place
        """
        def _move():
            self.place(anchor='s',
                relx=.5, rely=self.crnt_y_pos, relheight=self.height, relwidth=self.width)
            self.after(10, lambda: self.animate(animation_speed)) 

        if self.in_start_pos:
            if self.crnt_y_pos < self.final_pos:
                self.crnt_y_pos += animation_speed
                _move()
                return
            self.move_btn.configure(text= f'/ {self.move_btn_txt} \\')
            self.in_start_pos = not self.in_start_pos
        else:
            if self.crnt_y_pos > self.init_y_pos:
                self.crnt_y_pos -= animation_speed
                _move()
                return
            self.move_btn.configure(text= f'\\ {self.move_btn_txt} /')
            self.in_start_pos = not self.in_start_pos
    
    def on_color_picked(self , color: str) -> None:
        """
        Triggered by Signal.COLOR.
        """
        #TODO: see for decoupling, the mangling due to the GraphsParameter, signal?!; This is justified due to the inherent coupling of [self] and [master], as this is the only [master] of [self]; for now at least!!---> Implemented a function dependency injection.
        self._graph_parms.update(graph_color=color)
        self._con_func(self._graph_parms)

    def enable(self) -> None:
        """
        Makes the bar interactable.
        """
        if self.move_btn.cget('state') == ctk.DISABLED:
            self.move_btn.configure(state=ctk.NORMAL)
            self.htt_tip(self.move_btn, 'click to edit the graphs, color, etc,...')

        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 