from typedefs import GraphType, PlotData, SampleStats, StatsInterpretation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections.abc import Callable
from helpers import Analyzer, Plotter
from matplotlib.axes import Axes
from models import Sample

import matplotlib.pyplot as plt
import customtkinter as ctk
import tkinter as tk

class AnalysisPanal(ctk.CTkFrame):
    '''
    CTkFrame:
    The class that handels viewing and analyzing the data.
        - display the sample graphs [gaph_panal: ctk.CTkLabel].
        - display the sample data and the analysis result [data_panal: AnalysisBook]
    '''
    def __init__(self, master: ctk.CTkFrame) -> None:
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
        '''
        Triggered by an outside signal.
        '''
        self._create_analyzer(sample)
        #? is this the best place for this? NO, actually it might
        self.graph_panal.draw_graphs(self.analyzer, sample.get_name(), graph_type)      

    def write(self, sample: Sample, graph_type: GraphType|None) -> None:
        '''
        Triggered by an outside signal.
        '''
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
        _fig, _ax = plt.subplots()
        _fig.set_layout_engine('constrained')
        _canvas = FigureCanvasTkAgg(_fig, self.graph_frame) 
        _graph_name = self.graph_names[graph_type]

        _title: str = f"{_graph_name}\n{sample_name}"

        self.x, self.y, self.points = plot_data
        Plotter(self.x, self.y, self.points, _ax, graph_type, color)
                     
        _ax.set_title(_title)
        plt.close()

        return _canvas.get_tk_widget()

    def _set_graph_params(self, analyzer: Analyzer, sample_name: str,
                          graph_type: GraphType|None, graph_color: str = '#1f7bb4') -> None:
        '''
        Saves the current params used to produce the graph as a praph_params dict.
        '''
        self.graph_params: dict = {}

        self.graph_params['analyzer'] = analyzer
        self.graph_params['sample_name'] = sample_name
        self.graph_params['graph_type'] = graph_type
        self.graph_params['graph_color'] = graph_color

    def get_graph_params(self) -> dict:
        '''
        Returns the graph_params.
        '''
        return self.graph_params

    def update_graphs(self, graph_params: dict) -> None:
        '''
        Redraws the graph usin the new parameters.
        '''
        self.draw_graphs(**graph_params)

    def draw_graphs(self,
                    analyzer: Analyzer, sample_name: str,
                    graph_type: GraphType|None, graph_color:str = '#1f7bb4') -> None:
        '''
        Layout the graphs:
        - graph_type = None -> layout all the graphs in enums.GraphType.
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
        
        self._set_graph_params(analyzer, sample_name, graph_type)
        self.cust_bar.enable()


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
        _ana_method: str = analyzer.get_method()
        
        self.data_note.update_note(_sample_data_msg)
        self.stats_note.update_note(_stats_msg, _interp_msg, _ana_method)

#TODO make it a table, TreeView, parent with file picker??, maybe not, as we don't need to select here!
class DataNote(ctk.CTkTextbox):
    '''
    CTkTextbox
    '''
    def __init__(self, master: DataPanal, font: ctk.CTkFont) -> None:
        super().__init__(master)
        self.configure(state=ctk.DISABLED, font=font, tabs=150)  

    def update_note(self, text: str ) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert("1.0", text)
                self.configure(state=ctk.DISABLED)  


class StatsNote(ctk.CTkTextbox):
    '''
    CTkTextbox
    '''
    def __init__(self, master: DataPanal, font: ctk.CTkFont) -> None:
        super().__init__(master)
        self.configure(state=ctk.DISABLED, font=font, tabs=95)    

    def update_note(self, stats: str, interpretation: str, analysis_method: str) -> None:
                
                self.configure(state=ctk.NORMAL)
                self.delete("1.0", "end")
                self.insert(self.index(tk.INSERT), "-Stats:\n")
                self.insert(self.index(tk.INSERT), stats)
                self.insert(self.index(tk.INSERT), "\n")
                self.insert(self.index(tk.INSERT), "-Interpretation:\n")
                self.insert(self.index(tk.INSERT), interpretation)
                self.insert(self.index(tk.INSERT), "[Method Used]: ")
                self.insert(self.index(tk.INSERT), analysis_method)
                self.configure(state=ctk.DISABLED)  


class CustomizationBar(ctk.CTkFrame):
    '''
    CkFrame:
        Gives the ability to change the graph preview visuals.
    '''
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

    def _update_graphs(self, graph_params: dict) -> None:
        '''
        Delegates the graph update process to master: GraphPanal
        '''
        self.master.update_graphs(graph_params)

    def animate(self) -> None:
        '''
        Animates self into place
        '''
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
    
    def update_graph_params_clr(self , color: str) -> None:
        '''
        Triggerd by a preview button press From the clr_pikr: ColorPicker.
        '''
        graph_params: dict = self.master.get_graph_params()
        graph_params['graph_color'] = color
        self._update_graphs(graph_params)

    def enable(self) -> None:
        '''
        Make interactable.
        '''
        if self.move_btn.cget('state') == ctk.DISABLED:
            self.move_btn.configure(state=ctk.NORMAL)


class ColorPicker(ctk.CTkFrame):
    '''
    CTkFrame:
        An (RGB) color picker.
    '''
    def __init__(self, master: CustomizationBar) -> None:
        super().__init__(master)

        self.columnconfigure(0, weight=1, uniform='b')
        self.columnconfigure(1, weight=2, uniform='b')
        self.rowconfigure(0, weight=1, uniform='b')
        self.rowconfigure(1, weight=1, uniform='b')
        self.rowconfigure(2, weight=1, uniform='b')

        self.color: str = '#000000'

        self.preview: ctk.CTkButton = ctk.CTkButton(self,
                text='set', border_color='red', border_width=2,
                command= lambda: self._update_color(master, self.color))

        _r: ctk.IntVar = ctk.IntVar(self, value=138)
        _g: ctk.IntVar = ctk.IntVar(self, value=117)
        _b: ctk.IntVar = ctk.IntVar(self, value=216)

        self._set_color((_r,_g,_b))

        _r_slider: ColorSlider = ColorSlider(self, 'r', _r, lambda _: self._set_color((_r,_g,_b)))
        _g_slider: ColorSlider = ColorSlider(self, 'g', _g, lambda _: self._set_color((_r,_g,_b)))
        _b_slider: ColorSlider = ColorSlider(self, 'b', _b, lambda _: self._set_color((_r,_g,_b)))
    
        self.preview.grid(column=0, row=0, rowspan=3, padx=5, pady=2, sticky='nsew')
        _r_slider.grid(column=1, row=0, rowspan=1, padx=5)
        _g_slider.grid(column=1, row=1, rowspan=1, padx=5)
        _b_slider.grid(column=1, row=2, rowspan=1, padx=5)

        self.grid(column=0, row=0, sticky='nsew')

    def _set_color(self, rgb: tuple[ctk.IntVar,ctk.IntVar,ctk.IntVar]) -> None:
        '''
        Sets the color.
        '''
        clr: tuple[int,int,int] = tuple(i.get() for i in rgb)#type: ignore
        crnt_hvr_clr: list[str] = self.preview.cget('hover_color')
        
        self.color = '#'+''.join([f'{c:02x}' for c in clr])
        self.preview.configure(fg_color = self.color)

        if sum(clr) > 245:
            self.preview.configure(text_color = '#000000')
            self.preview.configure(hover_color=[crnt_hvr_clr[0],'#ffffff'])
        if sum(clr) < 245:
            self.preview.configure(text_color = '#ffffff')
            self.preview.configure(hover_color=[crnt_hvr_clr[0],'#000000'])

        if self.preview.cget('border_color') != 'red':
            self.preview.configure(border_color='red', text='set')

    def _update_color(self, master: CustomizationBar, color: str) -> None:
        '''
        Update the graph with the new color, delegated to master.
        '''
        master.update_graph_params_clr(color)
        self.preview.configure(border_color='green', text='set!')


class ColorSlider(ctk.CTkSlider):
    '''
    CTkSlider:
        For picking the color bandwise.
        - clr_band [str]:what band of the (R,G,B) band the slider represents.
        - variable [ctk.IntVar]:value to be adjusted through the slider.
        - command [Callable]:the behaviour to be linked with.
    '''
    def __init__(self,
                 master: ColorPicker, clr_band: str, variable: ctk.IntVar,
                 command: Callable) -> None:
        super().__init__(master)
        clrs: tuple[str, str, str] = ('','','')

        match clr_band:
            case 'r':
                clrs = ('#b50000', '#ff0000', '#855656')
            case 'g':
                clrs = ('#00b500', '#00ff00', '#568556')
            case 'b':
                clrs = ('#0000b5', '#0000ff', '#565685')

        self.configure(variable=variable, height=13,
            button_color=clrs[0], button_hover_color=clrs[1], progress_color=clrs[2],
            button_corner_radius=5, border_width=5, button_length=18,
            from_=0, to=255, number_of_steps=255, command=command)


        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 