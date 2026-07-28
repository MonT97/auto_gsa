# The various [type:: ignore] is due to an issue with pylance, the linter I use, for some reason, it thinks that _root() isn't a part of tkinter's base widget class [BaseWidget], although it clearly is!!
import traceback
from inspect import getfile, getsourcelines, signature
from tkinter import BaseWidget, Toplevel, Widget
from types import NoneType
from typing import TYPE_CHECKING, Any, Callable, Literal, get_args, overload

if TYPE_CHECKING:
    from models import Sample
    from typedefs import LogMsgType, GraphType, SaveObject

from models import SignalData
from typedefs import Signal
from utils import utls

_signals: dict[Signal, SignalData] = {}


class ArgumentsMismatch(Exception):
    """
    To prevent, at least in part, the silent failure when the listener func doesn't match the caller func's arguments by exposing relevant information in an error massage and suggesting a solution.
    """
    def __init__(self, signal: Signal, sender_args: list[Any],
                 func_args: list[Any], missing_args: list[Any], sender: Widget|None,
                 func: Callable|None, func_name: str = '',
                 func_location: str = '', func_line_number: int = 0) -> None:
        super().__init__()
        self._signal = signal

        self._sender_loc = sender
        self._send_args = sender_args
        
        self._func_name = func_name
        self._args = func_args
        
        self._missing_arg = missing_args

        if sender:
            self._sender_loc = getfile(sender.__class__)
        if func:
            self._func_name = func_name
            self._func_loc = func_location
            self._line_no = func_line_number
            self._args: list[Any] = [i.annotation for i in signature(func).parameters.values()]

    def __str__(self) -> str:

        _msg: str = ''

        if self._func_name:
            _msg =  f'Arguments type mismatch.\n    > signal {self._signal}: {self._send_args} != listeners {self._func_name}: {self._args}\n    > add [{len(self._missing_arg)}] argument of type/s {self._missing_arg} to the function [{self._func_name}] at: {self._func_loc}, line {self._line_no}'
        else:
            _msg = f'<!> Error: Arg Type mismatch {self._signal}: {self._send_args} != {self._args}\n    > missing [{len(self._missing_arg)}] of type/s {self._missing_arg} at: {self._sender_loc}'

        return _msg


class Observer():
    """
    A signal communication system.
    - broadcast using [obs_broadcast].
    - listen using [obs_listen]
    """
    def _validate_input(self, signal: Signal, sender: Widget|None = None,
                        sender_args: list[Any] = [], func: Callable|None = None) -> None:
        """
        Validates that the [signal] and the paired [args] or [func] have a match number of arguments.
        """
        _func_name = ''
        _missing_args = []
        _func_args = sender_args
        _signal = signal
        _sig_args = list(_signal.value.args)

        if func:
            _func_name = func.__qualname__
            _func_loc = func.__code__.co_filename
            _line_no = getsourcelines(func)[-1]
            _func_args: list[Any] = [i.annotation for i in signature(func).parameters.values()]
       
        _get_list: Callable = lambda x: x.value.args if isinstance(x, Signal) else x
        _clear_nons: Callable = lambda x: [i for i in x if NoneType not in get_args(i)]

        _M_args = _clear_nons(_get_list(max(_func_args, _signal)))
        _m_args = _clear_nons(_get_list(min(_func_args, _signal)))

        if len(_M_args) != len(_m_args):
            _ind = len(_M_args) - len(_m_args)
            _missing_args = _M_args[-_ind:]

        if _missing_args:
            raise ArgumentsMismatch(signal, 
                                    _sig_args, _func_args,_missing_args, sender,
                                    func, _func_name, _func_loc, _line_no)

    def _set_broadcast_data(self, signal: Signal, sender: BaseWidget, args: list[Any]) -> None:
        """
        Adds a signal named [signal_name] to [_signals] then creates a SignalData() and populates its [sender] and [arg] attributes.
        """        
        _signals.setdefault(signal, SignalData())
        _signal: SignalData = _signals[signal]
        _signal.add_arg(args)
        _signal.set_sender(sender)
    
    def _set_listener_data(self, signal: Signal, listener: BaseWidget) -> None:
        """
        Populates the [listener] and the related attributes of the SignalData object within _signals[signal_name].
        """
        _signals.setdefault(signal, SignalData())
        _signal: SignalData = _signals[signal]
        _signal.add_listener(listener)
    
    # These overloads mirror the SignalSchemas in typedefs.enum!
    @overload
    def obs_broadcast(self, signal: Literal[Signal.EXPORTED], sender: BaseWidget) -> None:
        """
        A function from the Observer mixin.
        Creates and broadcasts a signal.
        - signal: Signal.Exported.
        - sender: the signal broadcaster.
        - args: arguments to send for the listener function.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.COLOR], sender: BaseWidget,
                            args: tuple[str]) -> None:
        """
        A function from the Observer mixin.
        Creates and broadcasts a signal.
        - signal: Signal.COLOR.
        - sender: the signal broadcaster.
        - args: arguments to send for the listener function.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.LOG], sender: BaseWidget,
                            args: tuple[str, 'LogMsgType']) -> None:
        """
        A function from the Observer mixin.
        Creates and broadcasts a signal.
        - signal: Signal.LOG.
        - sender: the signal broadcaster.
        - args: arguments to send for the listener function.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.ANALYZE], sender: BaseWidget,
                            args: tuple['Sample', 'SaveObject', 'GraphType|None']) -> None:
        """
        A function from the Observer mixin.
        Creates and broadcasts a signal.
        - signal: Signal.ANALYZE.
        - sender: the signal broadcaster.
        - args: arguments to send for the listener function.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.EXPAND], sender: BaseWidget,
                            args: tuple[Widget]) -> None:
        """
        A function from the Observer mixin.
        Creates and broadcasts a signal.
        - signal: Signal.EXPAND.
        - sender: the signal broadcaster.
        - args: arguments to send for the listener function.
        """
    ...
    def obs_broadcast(self, signal: Signal, sender: BaseWidget,
                      args: tuple[Any,...]|None = None) -> None:
        """
        A function from the Observer mixin.
        Creates and broadcasts a signal.
        - signal: from the Signal enum.
        - sender: the signal broadcaster.
        - args: arguments to send for the listener function.
        """
        _args: list[Any] = list(args) if args else []
        self._validate_input(signal, sender_args=_args)

        _signal_name: str = signal.name
        _top_level: Toplevel = utls.get_root(sender)
        self._set_broadcast_data(signal, sender, _args)
        _top_level.event_generate(f'<<{_signal_name}>>')

    def obs_listen(self, signal: Signal, listener: BaseWidget, func: Callable) -> None:
        """
        A function from the Observer mixin.
        Listens for a broadcasted signal.
        - signal: from the Signal enum.
        - listener: the broadcast listener.
        - func: the listener function to be called.
        """
        self._validate_input(signal, func=func)

        _signal_name: str = signal.name
        _top_level: Toplevel = utls.get_root(listener)
        self._set_listener_data(signal, listener)
        _top_level.bind(f'<<{_signal_name}>>', lambda _: self._bind_func(signal, func), add='+')
        
    def _bind_func(self, signal: Signal, func: Callable) -> None:
        """
        Binds the function and handles the errors if the arguments miss match.
        """
        _signal = _signals[signal]
        _args = _signal.pop_arg()
        
        try:
            func(*_args)
        except Exception as e:
            print(f'<!> Error: {e}\n\n{traceback.print_exc()}')