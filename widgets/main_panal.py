from .analysis_panal import AnalysisPanal
from .log_pannal import LoggingLabel
from .file_panal import FilePanal

import customtkinter as ctk

class MainPanal(ctk.CTkFrame):
    """
    The applicatoin's main panal.
    """
    def __init__(self, master: ctk.CTk):
        super().__init__(master)
        self.file_panal: FilePanal = FilePanal(self)
        self.analysis_panal: AnalysisPanal = AnalysisPanal(self)
        self.logging_label: LoggingLabel = LoggingLabel(self)

        self._layout()

        # Inter-widget communication, signature <<Source-Action>>:
        self.winfo_toplevel().bind("<<FilePanal-log>>", lambda _: self.log())
        self.winfo_toplevel().bind("<<FilePanal-analyze>>", lambda _: self.analyze())
        self.winfo_toplevel().bind("<<FilePanal-exported>>", lambda _:self.exported())
        self.winfo_toplevel().bind("<<Screens-saved>>", lambda _: self.saved())
        self.winfo_toplevel().bind("<<AnalysisPanal-color>>", lambda _: self.update_color())
        self.winfo_toplevel().bind("<<LoggingPanal-zoom>>", lambda _: self.expand_log("log"))

    def _layout(self) -> None:
        """
        The original layout.
        """
        self.zoom: bool = False

        self.file_panal.place(anchor='nw', relx=0, rely=0, relwidt=.24, relheight=.95)
        self.analysis_panal.place(anchor='ne', relx=1, rely=0, relwidt=.76, relheight=.95)
        self.logging_label.place(anchor='sw', relx=0, rely=1, relwidth=1, relheight=.05)

    def log(self) -> None:
        """
        Log the massage into the logging widget; signal triggered.
        """
        _msg = self.file_panal.get_log_massage()
        self.logging_label.write(_msg)

    def analyze(self) -> None:
        """
        Tells the analysis widget to analyze the sample; signal triggered.
        """
        _sample, _graph_type = self.file_panal.get_analysis_data()

        self.analysis_panal.write(_sample, _graph_type)
        self.analysis_panal.draw_graphs(_sample, _graph_type)    

    def exported(self) -> None:
        """
        Tells the export screen; signal triggered. 
        """
        self.file_panal.on_exported()

    def saved(self) -> None:
        """
        Triggers the saving function; signal triggered.
        """
        self.file_panal.save_all()
    
    def update_color(self) -> None:
        """
        Tells the save object about the graph color; signal triggered.
        """
        _color: str = self.analysis_panal.get_graph_color()
        self.file_panal.update_save_obj_color(_color)
        
    def expand_log(self, widget_name: str) -> None:
        """
        Expand the [widget_name]; signal triggered.
        """
        # Any other widgets needs, in other words, do we need a match statment?
        if self.zoom:
            self._layout()
            return

        match widget_name:
            case "log":
                self.logging_label.place(anchor='sw', relx=0, rely=1, relwidth=1, relheight=.5)
                self.zoom = True
 
    def on_close(self) -> None:
        """
        Call delegated to master.
        """
        self.logging_label.on_close()

    def on_open(self) -> None:
        """
        Call delegated to master.
        """
        self.logging_label.on_open()