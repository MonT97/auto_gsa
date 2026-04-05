from widgets import MainPanal
from platform import system

import customtkinter as ctk

if system() != "Windows":
    print("Running in non-Windows OS, some eyecandy won't be visible!")


class App(ctk.CTk):
    """
    The application.
    """
    def __init__(self, title:str="AutoGSA", size:tuple[int,int]=(800,550)) -> None:
        super().__init__()
        #This is a hard coded value; trail&error driven.
        self.pos: tuple[int,int] = (
            self.winfo_screenwidth()//6,
            self.winfo_screenheight()//6)
        
        self.title(title)
        self.resizable(False, False)
        self.iconbitmap("assets/icon.ico")
        self.geometry(f"{size[0]}x{size[1]}+{self.pos[0]}+{self.pos[1]}")
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_panal: MainPanal = MainPanal(self)
        self.main_panal.pack(expand=1, fill='both')
        
        self.on_open()

    def on_open(self) -> None:
        """
        Triggered on application launch.
        """
        self.main_panal.on_open()

    # TODO[LTS]: see if you can hide/handle the stuff chucked into the stdo, it seems fine now!!
    def on_closing(self) -> None:
        """
        Triggered on application closure.
        """
        self.quit()
        self.main_panal.on_close()
        self.destroy()

    def run(self) -> None:
        """
        Run the application.
        """
        self.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()