# Due to the way tkinter handles event bindings race conditions are bound to happen, in which a listener might be added before the broadcaster/sender leading to a situation where we don't know the [args] to listen to, hence the convoluted args logic resulting from the need to handle multiple entry points to append new [arg] to [self.args]!!
from tkinter import BaseWidget
from tkinter.commondialog import Dialog
from typing import Any


class SignalData():
    """
    A class that holds signal data, use:
    - `add_args`: adds arguments into the signal data.
    - `add_listener`: adds a listener into the signal data.
    - `set_sender`: adds a sender into the signal data.
    - `pop_arg`: retrieves an argument from the args. 
    """
    def __init__(self) -> None:
        """
        A class that holds signal data, it holds:
        - sender.
        - listener.
        - args.
        """
        self.sender: Dialog|BaseWidget|None = None
        self.listeners: list[BaseWidget|Dialog] = []
        self.args: list[list[Any]] = [[]]
    
    def __repr__(self) -> str:
        return f'{self.__dict__}'

    def add_arg(self, arg: list[Any]) -> None:
        """
        Adds [arg] to self and handles the issue of multiple listeners and the case where the listener subs before the broadcast, which almost always the case. 
        """
        # max to avoid accidentally nullifying [self.args] by *= 0 or range(0).
        _n_listeners: int = max(len(self.listeners),1)
        _temp_arg: list[Any] = self.args[0] if self.args else arg

        # this corrects for the number of listeners, as the [add_arg] is linked to [set_sender]
        if len(self.args) != _n_listeners:
            self.args = [_temp_arg for i in range(_n_listeners)]

        if arg != _temp_arg:
            self.args = [arg for arg_ in self.args]
        
    def add_listener(self, listener: BaseWidget|Dialog) -> None:
        """
        Adds a listener.
        """
        self.listeners.append(listener)
    
    def set_sender(self, sender: BaseWidget|Dialog) -> None:
        """
        Adds a sender.
        """
        self.sender = sender
    
    def pop_arg(self) -> list[Any]:
        """
        Gets an argument from [self.args].
        """
        return self.args.pop(-1)