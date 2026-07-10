from typing import Any

import customtkinter as ctk

from mixins import Observer

from .analysis_panal import AnalysisPanal
from .file_panal import FilePanal
from .log_pannal import LoggingLabel


class MainPanal(ctk.CTkFrame, Observer):
    """
    The applicatoin's main panal.
    """
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        #! Still not sure about this!
        self.columnconfigure(0, weight=4, uniform='a')
        self.columnconfigure(1, weight=13, uniform='a')
        self.rowconfigure(0, weight=23, uniform='b')
        self.rowconfigure(1, weight=1, uniform='b')

        self.file_panal: FilePanal = FilePanal(self)
        self.analysis_panal: AnalysisPanal = AnalysisPanal(self)
        self.logging_label: LoggingLabel = LoggingLabel(self)

        self._layout()

        #TODO: expirement with custom singelton comm system! [LTS].
        # Inter-widget communication, signature <<Observer Source-Action to make>>:
        self.obs_listen('FilePanal-log', self, self.log)
        self.obs_listen('Screens-saved', self, self.saved)
        self.obs_listen('FilePanal-analyze', self, self.analyze)
        self.obs_listen('FilePanal-exported', self, self.exported)
        self.obs_listen("LoggingPanal-zoom", self, self.expand_log)
        self.obs_listen('AnalysisPanal-color', self, self.update_color)

    def _layout(self) -> None:
        """
        The original layout.
        """
        self.zoom: bool = False

        self.file_panal.grid(column=0, row=0, sticky='nsew')
        self.analysis_panal.grid(column=1, row=0, sticky='nsew')
        self.logging_label.grid(column=0, row=1, columnspan=2, sticky='nsew')

    def log(self, msg) -> None:
        """
        Log the massage into the logging widget; signal triggered.
        """
        self.logging_label.write(msg)

    def analyze(self, sample, graph_type: Any|None = None) -> None:
        """
        Tells the analysis widget to analyze the sample; signal triggered.
        """
        self.analysis_panal.write(sample, graph_type)
        self.analysis_panal.draw_graphs(sample, graph_type) #type: ignore 

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
    
    def update_color(self, color) -> None:
        """
        Tells the save object about the graph color; signal triggered.
        """
        self.file_panal.update_save_obj_color(color)
        
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