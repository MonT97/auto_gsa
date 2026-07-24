# The various [type:: ignore] is due to an issue with pylance, the linter I use, for some reason, it thinks that _root() isn't a part of tkinter's base widget class [Misc], although it clearly is!!
from inspect import getsourcelines, signature
from tkinter import Misc, Toplevel
from typing import Any, Callable

from models import SignalData

_signals: dict[str, SignalData] = {}

class Observer():
    """
    A signal communication system.
    - broadcast using [obs_broadcast].
    - listen using [obs_listen]
    """
    def _set_broadcast_data(self, signal_name: str, sender: Misc, args: list) -> None:
        """
        Adds a signal named [signal_name] to [_signals] then creates a SignalData() and populates its [sender] and [arg] attributes.
        """        
        _signals.setdefault(signal_name, SignalData())
        _signal: SignalData = _signals[signal_name]
        _signal.add_arg(args)
        _signal.set_sender(sender)
    
    def _set_listener_data(self, signal_name: str, listener: Misc, func: Callable) -> None:
        """
        Populates the [listener] and the various [func] related attributes of the SignalData object within _signals[signal_name].
        """
        # we can't be sure if the broadcaster proceeded the listener, hence the 2 lines bellow:
        _signals.setdefault(signal_name, SignalData())
        _signal: SignalData = _signals[signal_name]
        _signal.add_listener(listener)
    
    def obs_broadcast(self, signal_name: str, sender: Misc, args: list[Any] = []) -> None:
        """
        Creates and broadcasts a signal.
        - signal_name: the name of the signal.
        - sender: the signal broadcaster.
        - args: arguments to send for the listener function.
        """
        _top_level: Toplevel = sender._root() #type: ignore
        self._set_broadcast_data(signal_name, sender, args)
        _top_level.event_generate(f'<<{signal_name}>>')

    def obs_listen(self, signal_name: str, listener: Misc, func: Callable) -> None:
        """
        Listens for a broadcasted signal.
        - signal_name: the name of the signal.
        - listener: the broadcast listener.
        - func: the listener function to be called.
        """
        _top_level: Toplevel = listener._root() #type: ignore
        self._set_listener_data(signal_name, listener, func)
        _top_level.bind(f'<<{signal_name}>>', lambda _: self._bind_func(signal_name, func), add='+')
        
    def _bind_func(self, signal_name: str, func: Callable) -> None:
        """
        Binds the function and handles the errors if the arguments miss match.
        """
        _signal = _signals[signal_name]
        _sender = _signal.sender

        _args = _signal.pop_arg()
        _n_args = len(_args)
        _args_types = [type(i) for i in _args]

        _func_loc = func.__code__.co_filename
        _func_line = getsourcelines(func)[-1]
        _func_args = list(signature(func).parameters.values())
        _n_func_args = len(_func_args)
        try:
            func(*_args)
        except TypeError as e:
            # to prevent, partially at least, the silent failure when the listener func doesn't match the caller func's arguments by exposing relevant information in an error massage and suggesting a solution.
            print(f'<!> {__name__}\n\tError msg: {e}\n\tSender: {_sender} --< {signal_name} >--> Listener: {func.__qualname__}\n\tListener\'s func args: {_func_args}\n  > Refactor the listener func [{func.__qualname__}] at [{_func_loc}, line {_func_line}]:\n\tShould accept [{_n_args}] parameters of types {_args_types}\n\tjust matching the number of parameters from [{_n_func_args}] to [{_n_args}] is enough.')