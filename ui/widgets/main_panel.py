import inspect
from tkinter import Widget
from typing import TYPE_CHECKING, Literal

import customtkinter as ctk

from mixins import Observer
from models import Sample
from typedefs import GraphType, LogMsgType, SaveObject, Signal

from .analysis_panel import AnalysisPanel
from .file_panel import FilePanel
from .log_panel import LoggingLabel

if TYPE_CHECKING:
    from models import Analyzer


class MainPanel(ctk.CTkFrame, Observer):
    """
    The application's main panel.
    """
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        #! Still not sure about this!
        self.columnconfigure(0, weight=4, uniform='a')
        self.columnconfigure(1, weight=13, uniform='a')
        self.rowconfigure(0, weight=23, uniform='b')
        self.rowconfigure(1, weight=1, uniform='b')

        self.file_panel: FilePanel = FilePanel(self)
        self.analysis_panel: AnalysisPanel = AnalysisPanel(self)
        self.logging_label: LoggingLabel = LoggingLabel(self)

        self._layout()

        self.obs_listen(Signal.LOG, self, self.log)
        self.obs_listen(Signal.ANALYZE, self, self.analyze)
        self.obs_listen(Signal.EXPORTED, self, self.exported)
        self.obs_listen(Signal.EXPAND, self, self.expand_log)
        self.obs_listen(Signal.COLOR, self, self.update_color)

    def _layout(self) -> None:
        """
        The original layout.
        """
        self.zoom: bool = False

        self.file_panel.grid(column=0, row=0, sticky='nsew')
        self.analysis_panel.grid(column=1, row=0, sticky='nsew')
        self.logging_label.grid(column=0, row=1, columnspan=2, sticky='nsew')

    def log(self, msg: str, prefix: LogMsgType|None=None) -> None:
        """
        Log the massage into the logging widget; signal triggered.
        """
        self.logging_label.write(msg, prefix)

    def analyze(self, sample: Sample, save_obj: SaveObject,
                graph_type: GraphType|None=None) -> None:
        """
        Tells the analysis widget to analyze the sample; signal triggered.
        """
        self.analysis_panel.write(sample, graph_type)
        self.analysis_panel.draw_graphs(sample, save_obj, graph_type)

    def exported(self) -> None:
        """
        Tells the export screen; signal triggered. 
        """
        self.file_panel.on_exported()
    
    def update_color(self, color: str) -> None:
        """
        Tells the save object about the graph color; signal triggered.
        """
        self.file_panel.update_color_obj(color)
        
    def expand_log(self, widget: Widget) -> None:
        """
        Expand the [widget_name]; signal triggered.
        """
        # Any other widgets needs, in other words, do we need a match statement?
        if self.zoom:
            self._layout()
            return
        
        widget.place(anchor='sw', relx=0, rely=1, relwidth=1, relheight=.5)
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