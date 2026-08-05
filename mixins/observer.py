# The various [type:: ignore] is due to an issue with pylance, the linter I use, for some reason, it thinks that _root() isn't a part of tkinter's base widget class [BaseWidget], although it clearly is!!
from inspect import getfile, getsourcelines, signature
from tkinter import Toplevel, BaseWidget
from tkinter.commondialog import Dialog
from types import NoneType, UnionType
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
                 func_args: list[Any], sender: Dialog|BaseWidget|None, func: Callable|None,
                 func_name: str, func_location: str, func_line_number: int,
                 type_str: dict[int,Any], args_to_add: dict[int,Any],
                 args_to_remove: dict[int,Any]) -> None:
        """
        - type_str: TYPE_CHECKING strings.
        """
        super().__init__()
        self._error_msg: str = ''

        self._signal = signal

        self._sender = sender
        self._sender_loc = sender
        self._send_args = sender_args
        
        self._func_name = func_name
        
        self._args_to_add = args_to_add
        self._args_to_remove = args_to_remove
        self._type_str = type_str
        self._args = func_args if func else {i: type(i) for i in func_args}

        if self._sender:
            self._sender_loc = getfile(sender.__class__)
            self._args_to_remove = list(self._args_to_remove.values())
        if func:
            self._func_name = func_name
            self._func_loc = func_location
            self._line_no = func_line_number
        
        self._error_msg = self._set_error_msg()

    def _set_error_msg(self) -> str:
        _msg: str = f'<!> {__name__} ArgumentsMissmatch Error:'
        _warn: str = '\n<!> Warning:'
        _fix: str = '\n<!> Fix:'
        _loc: str = '\n  > Location: '
        _entity: str = ''
        _t_strs: str = ''

        # setting the msg, location and entity to adjust:
        if self._func_name:
            _msg +=  f'\n  > Signal name: [{self._signal}]\n  > Listener func name: [{self._func_name}]\n  > Signal args: {self._send_args}\n  > Listener func args: {self._args}\n  > Listeners args do not match the Signals arguments!'
            _loc += f'{self._func_loc}, line {self._line_no}'
            _entity = 'the Listener func'
        else:
            _msg += f'\n  > Signal name: [{self._signal}]\n  > Signal args: {self._send_args}\n  > Sender args {{value: type}} : {self._args}\n  > Senders args do not match the Signals arguments!'
            _loc += f'{self._sender_loc}'
            _entity = 'the Senders args'

        # setting the fix:
        if self._type_str:
            _t_strs = '\n'.join([f'  > arg: [{v}] at location [{k}]' for k, v in self._type_str.items()])
            _warn += f' TYPE_CHECKING strings were detected in the listeners function.\n{_t_strs}\n  > No accurate fix suggestion could be made!.\n  > Try to avoid using TYPE_CHECKING strings in signal related functions!.'
            return _msg+_warn+_loc
        if self._args_to_remove:
            if isinstance(self._args_to_remove, dict):
                _rem = '\n'.join([f'    > arg: [{v}] form location [{k}]' for k, v in self._args_to_remove.items()])
            else:
                _rem = f'    > args: {self._args_to_remove}'
            _fix += f'\n  > Remove [{len(self._args_to_remove)}] from {_entity}:\n{_rem}.'
        if self._args_to_add:
            _missing = '\n'.join([f'    > arg: [{v}] to location [{k}]' for k, v in self._args_to_add.items()])
            _fix += f'\n  > Add: [{len(self._args_to_add)}] args fallowing the next {{type: location}} schema to {_entity}:\n{_missing}'

        return _msg+_fix+_loc

    def __str__(self) -> str:
        return self._error_msg
    
    def __repr__(self) -> str:
        return self._error_msg


class Observer():
    """
    A signal communication system.
    - functions:
    - `obs_broadcast`: to broadcast.
    - `obs_listen`: to listen.
    """
    def _validate_input(self, signal: Signal, sender:BaseWidget|Dialog|None = None,
                        sender_args: list[Any] = [], func: Callable|None = None) -> None:
        """
        Validates that the [signal] and the paired [args] or [func] args have a matching number of arguments and matching argument types.
        - signal: from the Signal enum.
        - sender: the signal broadcaster.
        - sender_args: the arguments that the broadcaster sent with the signal.
        - func: the function which the listener tied into the [signal].
        - Assume there is no forwarded TYPE_CHECKING within the signal args!!.
        """
        _signal: Signal = signal
        _sig_args = list(_signal.get_args())

        _type_str: dict = {}
        _func_name: str = ''
        _func_loc: str = ''
        _line_no: int = 0
        _func_args = sender_args

        if func:
            _func_name = func.__qualname__
            _func_loc = func.__code__.co_filename
            _line_no = getsourcelines(func)[-1]
            _func_args: list[Any] = [i.annotation for i in signature(func).parameters.values()]
            
        def _get_forwarded_strs(list_: list[Any]) -> tuple[list[Any], dict[int,Any]]:
            """
            Parses the function arguments list [list_] in order to generate a dict for the forwarded TYPE_CHECKING strings and strip [list_] of said strings.
            -> tuple[stripped list, TYPE_CHECKING str as dict{location: value}]
            """
            _strip_list = list_.copy()
            _type_checking_strs = {}
            for loc, i in enumerate(list_):
                if isinstance(i, str):
                    _type_checking_strs[loc] = i
                    _strip_list.pop(loc)   
            return _strip_list, _type_checking_strs
        
        def _list_difference(sig_args: list[Any], sender_args: list[Any],
                  sender: bool = False) -> tuple[dict[int,Any],dict[int,Any]]:
            """
            Find the difference between [sig_args] and [sender_args] and returns the result, basically this is a position respecting version of the typical set difference operation [sig_args]/[sender_args].
            -> the difference as {location within [sig_args]: value} dict.
            """
            _add_k: list[int] = []
            _rem_k: list[int] = []

            _add: dict[int,Any] = {}
            _rem: dict[int,Any] = {}

            _is_ut = lambda x: isinstance(x, UnionType)
            _is_sub_class = lambda x, y: x in y.mro() 

            for ind, (i, j) in enumerate(zip(sig_args, sender_args)):
                j = type(j) if sender else j# sender passes values , hence the _is_sub_class
                is_i_ut, is_j_ut = _is_ut(i), _is_ut(j)
                _diff = False
                _val = i

                if sender:  
                    if is_i_ut and is_j_ut:
                        _i_ut, _j_ut = get_args(i), get_args(j)
                        for loc, i_ in enumerate(_i_ut):
                            if i_ not in _j_ut[loc].mro():
                                _diff = True
                                _val = i_
                    elif is_i_ut:
                        _diff = not any(_is_sub_class(x, j) for x in get_args(i))
                    elif is_j_ut:
                        _diff = not any(_is_sub_class(i, x) for x in get_args(j))
                    else:
                        _diff = i not in j.mro()
                else:
                    if is_i_ut and is_j_ut:
                        _diff = set(get_args(i)).isdisjoint(set(get_args(j)))
                    elif is_i_ut:
                        _diff = j not in get_args(i)
                    elif is_j_ut:
                        _diff = i not in get_args(j)
                    else:
                        _diff = i != j

                if _diff:
                    _add[ind] = _val
                    _rem[ind] = j
            
            _cond = lambda key,lst,x : (key in lst) and (NoneType not in get_args(x))
            
            _add_k= [i for i in range(len(sender_args), len(sig_args))]
            _rem_k= [i for i in range(len(sig_args), len(sender_args))]

            _add_keys = list(_add.keys())+_add_k
            _add = {k: v for k,v in enumerate(sig_args) if _cond(k,_add_keys, v)}

            _rem_keys = list(_rem.keys())+_rem_k
            _rem = {k: v for k,v in enumerate(sender_args) if _cond(k, _rem_keys, v)}

            return _add, _rem

        if not sender:
            _func_args, _type_str = _get_forwarded_strs(_func_args)

        # find the elements each arg list lacks relative to the other:

        # variable names here are relative to what should be done to conform to the signals args schema!
        _args_to_add, _args_to_rem = _list_difference(_sig_args, _func_args, bool(sender))
        
        try:
            _miss_match = bool(_args_to_add) or bool(_args_to_rem)
            if _miss_match:
                raise ArgumentsMismatch(signal,  _sig_args, _func_args, sender,
                                        func, _func_name, _func_loc, _line_no,
                                        _type_str, _args_to_add, _args_to_rem)
        except ArgumentsMismatch as e:
            print(e)
            quit()

    def _set_broadcast_data(self, signal: Signal, sender: Dialog|BaseWidget, args: list[Any]) -> None:
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
        - signal: Signal.Exported.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.COLOR], sender: BaseWidget,
                            args: tuple[str]) -> None:
        """
        - signal: Signal.COLOR.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.LOG], sender: BaseWidget|Dialog,
                            args: tuple[str, 'LogMsgType']) -> None:
        """
        - signal: Signal.LOG.
        """
    @overload
    def obs_broadcast(self, signal: Literal[Signal.LOG], sender: BaseWidget|Dialog, args: tuple[str]) -> None:
        """
        - signal: Signal.LOG.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.ANALYZE], sender: BaseWidget,
                            args: tuple['Sample', 'SaveObject', 'GraphType|None']) -> None:
        """
        - signal: Signal.ANALYZE.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.ANALYZE], sender: BaseWidget,
                            args: tuple['Sample', 'SaveObject']) -> None:
        """
        - signal: Signal.ANALYZE.
        """
    ...
    @overload
    def obs_broadcast(self, signal: Literal[Signal.EXPAND], sender: BaseWidget,
                            args: tuple[BaseWidget]) -> None:
        """
        - signal: Signal.EXPAND.
        """
    ...
    def obs_broadcast(self, signal: Signal, sender: BaseWidget|Dialog,
                      args: tuple[Any,...]|None = None) -> None:
        """
        A function from the Observer mixin.
        Creates and broadcasts a signal.
        - `signal`: from the Signal enum.
        - `sender`: the signal broadcaster.
        - `args`: arguments to send for the listener function.
        """
        _args: list[Any] = list(args) if args else []
        self._validate_input(signal, sender=sender, sender_args=_args)

        _signal_name: str = signal.get_name()
        _top_level: Toplevel = utls.get_root(sender)
        self._set_broadcast_data(signal, sender, _args)
        _top_level.event_generate(f'<<{_signal_name}>>')

    def obs_listen(self, signal: Signal, listener: BaseWidget, func: Callable) -> None:
        """
        A function from the Observer mixin.
        Listens for a broadcasted signal.
        - `signal`: from the Signal enum.
        - `listener`: the broadcast listener.
        - `func`: the listener function to be called.
        """
        if signal not in _signals:
            self._validate_input(signal, func=func)

        _signal_name: str = signal.get_name()
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
            print(f"{e}\n Past validation!\nsig name: {signal.get_name()}\nfunction: {func},\nargs: {_args}.")