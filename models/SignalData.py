# Due to the way tkinter handles event bindings race conditions are bound to happen, in which a listener might be added before the broadcaster/sender leading to a situation where we don't know the [args] to listen to, hence the convoluted args logic resulting from the need to handle multiple entry points to append new [arg] to [self.args]!!
from inspect import Signature, signature
from tkinter import Misc
from typing import Any, Callable


class SignalData():
    """
    A class that holds signal data, use:
    - [.add_args], [.add_listeners], [.set_sender] to set the signal data. 
    - [.pop_arg] to get arguments to pass to the listener function.
    """
    def __init__(self) -> None:
        """
        A class that holds signal data, use:
        - [.add_args], [.add_listeners], [.set_sender] to set the signal data. 
        - [.pop_arg] to get arguments to pass to the listener function.
        """
        self.added_func: bool = False
        self.sender: Misc|None = None
        self.listeners: list[Misc] = []
        self.args: list[list[Any]] = [[]]
    
    def __repr__(self) -> str:
        self.__dict__.pop('added_func')
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
        
    def add_listener(self, listener: Misc) -> None:
        """
        Adds a listener.
        """
        self.listeners.append(listener)
    
    def set_sender(self, sender: Misc) -> None:
        """
        Adds a sender.
        """
        self.sender = sender
    
    def pop_arg(self) -> list[Any]:
        """
        Gets an argument.
        """
        return self.args.pop(-1)