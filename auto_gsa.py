from widgets import FilePanal, AnalysisPanal
from platform import system

import customtkinter as ctk


if system() != "Windows":
    print("Running in non-Windows OS, some eyecandy won't be visible!")


class App(ctk.CTk):

    def __init__(self, title:str="AutoGSA", size:tuple[int,int]=(800,500)) -> None:
        super().__init__()

        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_panal: MainPanal = MainPanal(self)
        self.main_panal.pack(expand=1, fill='both')

    # TODO[LTS]: see if you can hide/handle the stuff chucked into the stdo
    def on_closing(self) -> None:

        self.quit()
        self.destroy()

    def run(self) -> None:

        self.mainloop()


class MainPanal(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        self.columnconfigure(0, weight=1, uniform="a")
        self.columnconfigure(1, weight=3, uniform="a")
        self.rowconfigure(0, weight=1, uniform="a")

        self.analysis_panal: AnalysisPanal = AnalysisPanal(self)
        self.file_panal: FilePanal = FilePanal(self)

        self.file_panal.grid(row=0, column=0, padx=2.5, pady=5, sticky="nwse")
        self.analysis_panal.grid(row=0, column=1, padx=2.5, pady=5, sticky="nwse")
    
        self.winfo_toplevel().bind("<<FilePanal-analyze>>", lambda _: self._analyze())

    def _analyze(self) -> None:

        sample, graph_type = self.file_panal.get_analysis_data()

        self.analysis_panal.write(sample, graph_type)
        self.analysis_panal.draw_graphs(sample, graph_type)


if __name__ == '__main__':
    app = App()
    app.run()