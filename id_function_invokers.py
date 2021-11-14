#! /usr/bin/python3
# -*- coding: utf-8 -*-
# Remote invoker
import atexit
import logging
import os
import pathlib
import platform
import rpyc
import signal
import sys
import threading
import traceback
from typing import Dict, TypeVar, Generic
from rpyc.utils.server import ThreadedServer
from id_classes_utils import subclasses_of, import_files_of_dir
from abc import abstractmethod

VERSION: str = '1.0'
DEFAULT_PORT: int = 8000
_AN_ERROR_OCCURRED_MSG: str = 'An error occurred: %s'
RPC_TIMEOUT: int = 300
ALLOW_PUBLIC_ATTRS: bool = True
ALLOW_PICKLE: bool = True


class IllegalInvocationException(Exception):
    """Base class for other exceptions"""
    pass


class FunctionProvider(object):

    def __init__(self, parent_logger: logging.Logger):
        self._logger = logging.getLogger(self.__class__.__name__)
        for handler in parent_logger.handlers:
            self._logger.addHandler(handler)
        self._logger.setLevel(parent_logger.level)
        self._logger.debug('Function provider %s initialized', self.__class__.__name__)


class FunctionProviderService(rpyc.Service):

    def __init__(self, parent_logger: logging.Logger):
        self._logger = logging.getLogger(self.__class__.__name__)
        for handler in parent_logger.handlers:
            self._logger.addHandler(handler)
        self._logger.setLevel(parent_logger.level)
        self._logger.debug('Function provider service %s initialized', self.__class__.__name__)

    def on_connect(self, conn: rpyc.Connection) -> None:
        self._logger.debug("Connection from client: %s" % conn)

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        self._logger.debug("Disconnection of client: %s" % conn)

    @abstractmethod
    def finalize(self) -> None:
        pass


class FunctionProviderServiceProxy(object):
    _EXPOSED_PREFIX: str = 'exposed_'
    _OBJ: str = '_obj'
    __slots__ = ["_obj", "__weakref__"]
    _special_names = [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
    ]

    def __init__(self, obj: FunctionProviderService):
        object.__setattr__(self, FunctionProviderServiceProxy._OBJ, obj)

    def __getattribute__(self, name):
        if name.startswith(FunctionProviderServiceProxy._EXPOSED_PREFIX):
            return getattr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ), name)
        return getattr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ), FunctionProviderServiceProxy._EXPOSED_PREFIX + name)

    def __delattr__(self, name):
        if name.startswith(FunctionProviderServiceProxy._EXPOSED_PREFIX):
            delattr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ), name)
            return
        delattr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ), FunctionProviderServiceProxy._EXPOSED_PREFIX + name)

    def __setattr__(self, name, value):
        if name.startswith(FunctionProviderServiceProxy._EXPOSED_PREFIX):
            setattr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ), name, value)
            return
        setattr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ), FunctionProviderServiceProxy._EXPOSED_PREFIX + name, value)

    def __nonzero__(self):
        return bool(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ))

    def __str__(self):
        return str(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ))

    def __repr__(self):
        return repr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ))

    @classmethod
    def _create_class_proxy(cls, theclass):
        """Creates a proxy for the given class"""

        def make_method(name):

            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, FunctionProviderServiceProxy._OBJ), name)(*args, **kw)

            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """Creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are passed to this class' __init__, so deriving classes can define an __init__ method of their own."""
        the_class = cls._create_class_proxy(obj.__class__)
        instance = object.__new__(the_class)
        the_class.__init__(instance, obj, *args, **kwargs)
        return instance


class Connection(object):

    def __init__(self, connection: rpyc.Connection, set_thread: bool=False):
        self.__connection: rpyc.Connection = connection
        self.__thread: threading.Thread = None
        if set_thread:
            self.__thread = rpyc.BgServingThread(connection)

    def get_connection(self) -> rpyc.Connection:
        return self.__connection

    def get_thread(self) -> threading.Thread:
        return self.__thread
    
    def is_closed(self) -> bool:
        return (self.__connection is None or self.__connection.closed) and (self.__thread is None or self.__thread.is_alive())
    
    def close(self) -> None:
        try:
            if self.__connection and not self.__connection.closed:
                self.__connection.close()
            self.__connection = None
        except Exception:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
        try:
            if self.__thread and not self.__thread.is_alive():
                self.__thread.stop()
            self.__thread = None
        except Exception:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)


import_files_of_dir(str(pathlib.Path(__file__).parent) + os.sep + 'function_providers')

T = TypeVar('T', bound=FunctionProvider)
DictOfThreadedServer = Dict[str, ThreadedServer]
DictOfConnection = Dict[str, Connection]


def is_raspberry_pi() -> bool:
    return platform.machine() in ('armv7l', 'armv6l')


class RpcRegistryService(rpyc.Service):

    def __init__(self, parent_logger: logging.Logger, host: str, port: int, services: dict):
        self.__logger = logging.getLogger(self.__class__.__name__)
        for handler in parent_logger.handlers:
            self.__logger.addHandler(handler)
        self.__logger.setLevel(parent_logger.level)
        self.__services: DictOfThreadedServer = dict()
        current_port: int = port + 1
        for k, v in services.items():
            current_port = current_port + 1
            self.__logger.debug('Creating service %s at %s:%s' % (k, host, current_port))
            self.__services[k] = ThreadedServer(v, port=current_port, protocol_config={'allow_public_attrs': False})

    def exposed_get_service_port(self, name: str) -> int:
        self.__logger.debug('Retrieving port of service %s' % name)
        if name in self.__services:
            server: ThreadedServer = self.__services[name]
            if server:
                if not server.active:
                    self.__logger.debug('Starting service %s at %s:%s' % (name, server.host, server.port))
                    server._start_in_thread()
                self.__logger.debug('Port is %s' % server.port)
                return server.port
        self.__logger.debug('Service not available')
        return -1

    def start(self) -> None:
        self.__logger.debug('Starting all services')
        for k, v in self.__services.items():
            if v.active:
                self.__logger.debug('Service %s already started' % k)
            else:
                self.__logger.debug('Starting service %s at %s:%s' % (k, v.host, v.port))
                v.start()

    def stop(self) -> None:
        self.__logger.debug('Stopping all services')
        for k, v in self.__services.items():
            if v.active:
                self.__logger.debug('Stopping service %s at %s:%s' % (k, v.host, v.port))
                v.close()
            else:
                self.__logger.debug('Service %s already stopped' % k)

    def on_connect(self, conn: rpyc.Connection) -> None:
        self.__logger.debug("Connection from client: %s" % conn)

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        self.__logger.debug("Disconnection of client: %s" % conn)


class FunctionInvokers(object):
    __logger: logging.Logger = None
    __providers: dict = dict()
    __registry: RpcRegistryService = None
    __connections: DictOfConnection = None
    __initialize_lock: threading.Lock = threading.Lock()
    __get_lock: threading.Lock = threading.Lock()
    __server: ThreadedServer = None
    __client: rpyc.Connection = None
    __host: str = None
    __port: int = None
    __mock: bool = False

    @staticmethod
    def initialize(parent_logger: logging.Logger, host: str=None, port: int=DEFAULT_PORT, server: bool=False):
        with FunctionInvokers.__initialize_lock:
            if not FunctionInvokers.__logger:
                FunctionInvokers.__logger = logging.getLogger(FunctionInvokers.__name__)
                for handler in parent_logger.handlers:
                    FunctionInvokers.__logger.addHandler(handler)
                FunctionInvokers.__logger.setLevel(parent_logger.level)
                # If host is specified, the RPC services and proxies must be created
                # Otherwise the providers will be used
                FunctionInvokers.__host = host
                FunctionInvokers.__port = port
                FunctionInvokers.__mock = not is_raspberry_pi()
                if host:
                    if server:
                        # Server
                        try:
                            for subclass in subclasses_of(FunctionProvider):
                                if subclass.__name__ in FunctionInvokers.__providers:
                                    continue
                                class_name: str = subclass.__name__ + 'Service'
                                if FunctionInvokers.__mock:
                                    class_name = subclass.__name__ + 'ServiceMock'
                                the_class = getattr(sys.modules[subclass.__module__], class_name)
                                FunctionInvokers.__logger.info('Instantiating: %s for provider: %s', the_class.__name__, subclass.__name__)
                                FunctionInvokers.__providers[subclass.__name__] = the_class(parent_logger)
                        except Exception as ex:
                            _, _, exc_traceback = sys.exc_info()
                            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
                            FunctionInvokers.__logger.error(ex)
                        FunctionInvokers.__logger.debug('Creating registry')
                        # Build RPC service associated to providers
                        FunctionInvokers.__registry = RpcRegistryService(parent_logger, host, port, FunctionInvokers.__providers)
                        # Build RPC server
                        FunctionInvokers.__server = ThreadedServer(FunctionInvokers.__registry, port=port, protocol_config={'allow_public_attrs': ALLOW_PUBLIC_ATTRS, 'allow_pickle':ALLOW_PICKLE})
                    else:
                        # Client
                        FunctionInvokers.__logger.debug('Connecting proxy to remote registry at %s:%s' % (host, port))
                        # Get RPC proxy associated to service
                        FunctionInvokers.__client = rpyc.connect(host, port, config={'sync_request_timeout': RPC_TIMEOUT, 'allow_public_attrs': ALLOW_PUBLIC_ATTRS, 'allow_pickle':ALLOW_PICKLE})
                        FunctionInvokers.__registry = FunctionInvokers.__client.root
                        FunctionInvokers.__connections = dict()
                else:
                    # Local
                    try:
                        for subclass in subclasses_of(FunctionProvider):
                            if subclass.__name__ in FunctionInvokers.__providers:
                                continue
                            class_name: str = subclass.__name__ + 'Service'
                            if FunctionInvokers.__mock:
                                class_name = subclass.__name__ + 'ServiceMock'
                            the_class = getattr(sys.modules[subclass.__module__], class_name)
                            FunctionInvokers.__logger.info('Instantiating: %s for provider: %s', the_class.__name__, subclass.__name__)
                            # Use of a proxy to call exposed methods directly
                            FunctionInvokers.__providers[subclass.__name__] = the_class(parent_logger)
                    except Exception as ex:
                        _, _, exc_traceback = sys.exc_info()
                        traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
                        FunctionInvokers.__logger.error(ex)

    @staticmethod
    def is_mock() -> bool:
        return FunctionInvokers.__mock

    @staticmethod
    def is_local() -> bool:
        return FunctionInvokers.__host is None or len(FunctionInvokers.__host) == 0

    @staticmethod
    def is_server() -> bool:
        return FunctionInvokers.__server

    @staticmethod
    def get_host() -> str:
        return FunctionInvokers.__host

    @staticmethod
    def get_port() -> int:
        return FunctionInvokers.__port

    @staticmethod
    def get_provider(value: Generic[T]) -> T:
        FunctionInvokers.__logger.debug('Searching provider %s' % value.__name__)
        with FunctionInvokers.__get_lock:
            if FunctionInvokers.is_local():
                FunctionInvokers.__logger.debug('Retrieving local invoker %s' % value.__name__)
                provider = FunctionInvokers.__providers[value.__name__]
                if provider:
                    return FunctionProviderServiceProxy(provider)
                FunctionInvokers.__logger.warning('Provider not found %s' % value.__name__)
                return None
            else:
                if value.__name__ in FunctionInvokers.__connections:
                    FunctionInvokers.__logger.debug('Retrieving proxy %s' % value.__name__)
                    return FunctionInvokers.__connections[value.__name__].get_connection().root
                # Client
                port: int = FunctionInvokers.__registry.get_service_port(value.__name__)
                if port <= 0:
                    FunctionInvokers.__logger.warning('Provider not found %s' % value.__name__)
                    return None
                FunctionInvokers.__logger.debug(
                    'Connecting proxy %s at %s:%s' % (value.__name__, FunctionInvokers.__host, port))
                c = rpyc.connect(FunctionInvokers.__host, port, config={"sync_request_timeout": RPC_TIMEOUT, 'allow_public_attrs': ALLOW_PUBLIC_ATTRS, 'allow_pickle':ALLOW_PICKLE})
                FunctionInvokers.__connections[value.__name__] = Connection(c, set_thread=True)
                return c.root

    @staticmethod
    def get_version() -> str:
        return VERSION

    @staticmethod
    def start() -> None:
        if FunctionInvokers.__server:
            if not FunctionInvokers.__server.active:
                FunctionInvokers.__logger.debug('Starting registry at %s:%s' % (FunctionInvokers.__host, FunctionInvokers.__port))
                FunctionInvokers.__server.start()
        else:
            raise IllegalInvocationException('Cannot start server, not configured as a server')

    @staticmethod
    def stop() -> None:
        try:
            if FunctionInvokers.__registry:
                FunctionInvokers.__registry.stop()
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            FunctionInvokers.__logger.error(ex)
        try:
            if FunctionInvokers.__providers:
                for k, v in FunctionInvokers.__providers.items():
                    FunctionInvokers.__logger.debug('Closing provider %s' % k)
                    v.finalize()
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            FunctionInvokers.__logger.error(ex)
        try:
            if FunctionInvokers.__connections:
                for k, v in FunctionInvokers.__connections.items():
                    if not v.is_closed():
                        FunctionInvokers.__logger.debug('Closing proxy %s' % k)
                        v.close()
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            FunctionInvokers.__logger.error(ex)
        try:
            if FunctionInvokers.__client:
                FunctionInvokers.__logger.debug('Stopping client')
                FunctionInvokers.__client.close()
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            FunctionInvokers.__logger.error(ex)
        try:
            if FunctionInvokers.__server:
                FunctionInvokers.__logger.debug('Stopping registry')
                FunctionInvokers.__server.active = False
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            FunctionInvokers.__logger.error(ex)


atexit.register(FunctionInvokers.stop)
signal.signal(signal.SIGINT, FunctionInvokers.stop)
signal.signal(signal.SIGTERM, FunctionInvokers.stop)
