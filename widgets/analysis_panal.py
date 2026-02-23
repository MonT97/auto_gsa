from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typedefs import GraphType, PlotData, SampleStats, StatsInterpretation
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
        self._create_analyzer(sample)
        #? is this the best place for this? NO, actually it might
        self.graph_panal.draw_graphs(self.analyzer, sample.get_name(), graph_type)      

    def write(self, sample: Sample, graph_type: GraphType|None) -> None:
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
    CkFrame: gives the ability to change the graph preview visuals.
    '''
    def __init__(self, master:GraphPanal,
                 width: float, height:float, anim_speed: float =.01) -> None:
        super().__init__(master)
        
        offset: float = 0

        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=3, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')

        self.master: GraphPanal = master
        self.anim_speed: float = anim_speed

        self.width = width
        self.height = height

        self.initial_pos = .07
        self.crnt_y_pos = self.initial_pos
        self.final_pos = self.height + offset

        self.in_start_pos:bool = True

        self.clr_pikr: ColorPicker = ColorPicker(self)

        self.move_btn_txt: str = 'configuration'
        self.move_btn: ctk.CTkButton = ctk.CTkButton(self, corner_radius=0,
                height=100, text=f'\\ {self.move_btn_txt} /', state=ctk.DISABLED,
                command=lambda: self.animate())
        
        self.clr_pikr.grid(column=0, row=0, sticky='nsew')
        self.move_btn.grid(column=0, row=1, sticky='nsew')

        self.place(anchor='s',
                relx=.5, rely=self.crnt_y_pos, relheight=self.height, relwidth=self.width)

    def _update_graphs(self, graph_params: dict) -> None:
        '''
        Delegates the graph update process to master: GraphPanal
        '''
        self.master.update_graphs(graph_params)

    def animate(self):
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
    CTkFrame: an (RGB) color picker.
    '''
    def __init__(self, master: CustomizationBar) -> None:
        super().__init__(master)

        #! admittedly a weak architectural choice, look for a better option!

        self.columnconfigure(0, weight=1, uniform='b')
        self.columnconfigure(1, weight=2, uniform='b')
        self.rowconfigure(0, weight=1, uniform='b')
        self.rowconfigure(1, weight=1, uniform='b')
        self.rowconfigure(2, weight=1, uniform='b')

        self.color: str = '#000000'

        self.preview = ctk.CTkButton(self,
                                     text='set', border_color='red', border_width=2,
                                     command= lambda: self._update_color(master, self.color))

        r: ctk.IntVar = ctk.IntVar(self, value=138)
        g: ctk.IntVar = ctk.IntVar(self, value=117)
        b: ctk.IntVar = ctk.IntVar(self, value=216)

        self._set_color((r,g,b))

        r_slider: ctk.CTkSlider = ctk.CTkSlider(self,
                height=13, button_corner_radius=5, border_width=5, button_length=18,
                button_color='#b50000', button_hover_color='#ff0000', progress_color='#855656',
                from_=0, to=255, number_of_steps=255, variable=r,
                command=lambda _: self._set_color((r,g,b)))
        g_slider: ctk.CTkSlider = ctk.CTkSlider(self,
                height=13, button_corner_radius=5, border_width=5, button_length=18,
                button_color='#00b500', button_hover_color='#00ff00', progress_color='#568556',
                from_=0, to=255, number_of_steps=255, variable=g,
                command=lambda _: self._set_color((r,g,b)))
        b_slider: ctk.CTkSlider = ctk.CTkSlider(self,
                height=13, button_corner_radius=5, border_width=5, button_length=18,
                button_color='#0000b5', button_hover_color='#0000ff', progress_color='#565685',
                from_=0, to=255, number_of_steps=255, variable=b,
                command=lambda _: self._set_color((r,g,b)))
    
        self.preview.grid(column=0, row=0, rowspan=3, padx=5, pady=2, sticky='nsew')
        r_slider.grid(column=1, row=0, rowspan=1, padx=5)
        g_slider.grid(column=1, row=1, rowspan=1, padx=5)
        b_slider.grid(column=1, row=2, rowspan=1, padx=5)

        self.grid(column=0, row=0, sticky='nsew')

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

    def _update_color(self, master: CustomizationBar, color: str) -> None:
        '''
        Update the graph with the new color, delegated to master.
        '''
        master.update_graph_params_clr(color)
        self.preview.configure(border_color='green', text='set!')

        #! add the analysis and the data results into the GUI - DONE👌
        #? add the option to save the image/graph and the related analysis results and organize it to make sense for the end user; maybe report ready format as a pdf -do research?!!
        #? how well the end game well be? - contemplate! 