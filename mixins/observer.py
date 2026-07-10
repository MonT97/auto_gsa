from tkinter import Toplevel
from typing import Any, Callable

_signals: dict[str, list[list[Any]]] = {}

class Observer():
    """
    A signal communication system.
    - broadcast using [obs_broadcast].
    - listen using [obs_listen]
    """
    def _set_args(self, signal_name: str, args: list) -> None:
        _signals.setdefault(signal_name, []).append(args)
    
    def _get_args(self, signal_name: str) -> list:
        return _signals[signal_name].pop(0)
    
    def obs_broadcast(self, signal_name: str, sender, args: list = []) -> None:
        """
        Create and broadcasts a signal.
        - signal_name: the name of the signal.
        - sender: the signal proadcaster.
        - args: arguments to send for the listener function.
        """
        _top_level: Toplevel = sender.winfo_toplevel()
        self._set_args(signal_name, args)
        _top_level.event_generate(f'<<{signal_name}>>')
    
    def obs_listen(self, signal_name: str, listener, func: Callable) -> None:
        """
        Listens for a broadcasted signal.
        - signal_name: the name of the signal.
        - listener: the broadcast listener.
        - func: the listener function to be called.
        """
        _top_level: Toplevel = listener.winfo_toplevel()
        _top_level.bind(f'<<{signal_name}>>', lambda _: self._bind_func(func, signal_name), add='+')
        
    def _bind_func(self, func, signal_name) -> None:
        _args = self._get_args(signal_name)
        func(*_args)