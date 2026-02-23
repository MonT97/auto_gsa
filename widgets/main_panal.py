import customtkinter as ctk

from .analysis_panal import AnalysisPanal
from .file_panal import FilePanal

class MainPanal(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        self.columnconfigure(0, weight=1, uniform="a")
        self.columnconfigure(1, weight=3, uniform="a")
        self.rowconfigure(0, weight=1, uniform="a")

        self.analysis_panal: AnalysisPanal = AnalysisPanal(self)
        self.file_panal: FilePanal = FilePanal(self)
        self.file_panal.set_analysis_panal(self.analysis_panal)

        self.analysis_panal.grid(row=0, column=1, padx=2.5, pady=5, sticky="nwse")
        self.file_panal.grid(row=0, column=0, padx=2.5, pady=5, sticky="nwse")