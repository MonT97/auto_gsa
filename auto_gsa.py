import os

import customtkinter as ctk

from widgets import MainPanel

if os.name != 'nt':
    print("Running in non-Windows OS, some eyecandy won't be visible!")


class App(ctk.CTk):
    """
    The application.
    """
    def __init__(self, title:str="AutoGSA", size:tuple[int,int]=(800,600)) -> None:
        super().__init__()
        #This is a hard coded value; trail&error driven.
        position: tuple[int,int] = (
            self.winfo_screenwidth()//6,
            self.winfo_screenheight()//6)
        
        self.title(title)
        self.resizable(False, False)
        self.iconbitmap("assets/icon.ico")
        self.geometry(f"{size[0]}x{size[1]}+{position[0]}+{position[1]}")
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_panel: MainPanel = MainPanel(self)
        self.main_panel.pack(expand=1, fill='both')
        
        self.on_open()

    def on_open(self) -> None:
        """
        Triggered on application launch.
        """
        self.main_panel.on_open()

    def on_closing(self) -> None:
        """
        Triggered on application closure.
        """
        self.quit()
        self.main_panel.on_close()
        self.destroy()

    def run(self) -> None:
        """
        Run the application.
        """
        self.mainloop()

if __name__ == '__main__':
    app = App()
    app.run()