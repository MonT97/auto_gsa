import customtkinter as ctk

in_windows:bool = True
try:
    from ctypes import windll, byref, c_int, sizeof
except Exception as e:
    in_windows = False
    print("Running in non-Windows OS, some eyecandy won't be visible!")

from widgets import FilePanal, AnalysisPanal

class App(ctk.CTk):

    def __init__(self, title:str="AutoGSA", size:tuple[int,int]=(800,500)):
        super().__init__()

        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.rowconfigure(0, weight=1, uniform="a")
        self.columnconfigure(0, weight=1, uniform="a")
        self.columnconfigure(1, weight=3, uniform="a")

        self.data_panal: ctk.CTkFrame = AnalysisPanal(self)
        self.file_panal: ctk.CTkFrame = FilePanal(self, self.data_panal)

        self.data_panal.grid(row=0, column=1, padx=2.5, pady=5, sticky="nwse")
        self.file_panal.grid(row=0, column=0, padx=2.5, pady=5, sticky="nwse")


    # TODO see if you can hide/handle the stuff chucked into the stdo
    def on_closing(self) -> None:

        self.quit()
        self.destroy()

    def run(self) -> None:

        self.mainloop()


app = App()
app.run()