from typing import Callable, Any, Awaitable, Generator, Self

import re

import inspect

import threading
import asyncio


type CallbackType[**P] = Callable[P, Any] | Callable[P, Awaitable[Any]]
type TimeoutType = int | float


class Event[**P]:
    def __init__(self):
        self.sync_callbacks: list[Callable[P, Any]] = []
        self.async_callbacks: list[Callable[P, Awaitable[Any]]] = []
        self.thread_condition = threading.Event()
        self.asyncio_condition = asyncio.Event()
        self.last_args: P.args = None
        self.last_kwargs: P.kwargs = None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.clear()
        for callback in self.sync_callbacks:
            callback(*args, **kwargs)
        for callback in self.async_callbacks:
            asyncio.get_running_loop().run_until_complete(callback(*args, **kwargs))
        self.last_args = args
        self.last_kwargs = kwargs
        self.set()

    def __iadd__(self, callback: CallbackType[P]) -> Self:
        if inspect.iscoroutinefunction(callback):
            self.async_callbacks.append(callback)
        else:
            self.sync_callbacks.append(callback)
        return self

    def __isub__(self, callback: CallbackType[P]) -> Self:
        if inspect.iscoroutinefunction(callback):
            self.async_callbacks.remove(callback)
        else:
            self.sync_callbacks.remove(callback)
        return self

    def __await__(self) -> Generator[Any, None, tuple[P.args, P.kwargs]]:
        return self.wait_async().__await__()

    async def wait_async(self) -> tuple[P.args, P.kwargs]:
        await self.asyncio_condition.wait()
        return self.last_args, self.last_kwargs

    def wait(self, timeout: TimeoutType = None) -> tuple[P.args, P.kwargs]:
        self.thread_condition.wait(timeout)
        return self.last_args, self.last_kwargs

    def set(self) -> None:
        self.thread_condition.set()
        self.asyncio_condition.set()

    def clear(self) -> None:
        self.thread_condition.clear()
        self.asyncio_condition.clear()


ON_CHANGED_PATTERN = re.compile(r'on_(.+)_changed')
ON_CHANGED_FORMAT = 'on_{name}_changed'


class ObservableConfig:
    def __getattr__(self, name: str) -> Any:
        match = re.match(ON_CHANGED_PATTERN, name)
        if not match:
            raise AttributeError(name)
        key = match.group(1)
        if not hasattr(self, key):
            raise AttributeError(f'No field called: {key} found for: {name}')
        event = Event()
        super().__setattr__(name, event)
        return event

    def __setattr__(self, name: str, value: Any):
        previous_value = getattr(self, name)
        super().__setattr__(name, value)
        if value == previous_value:
            return
        event = getattr(self, ON_CHANGED_FORMAT.format(name=name), None)
        if isinstance(event, Event):
            event(previous_value, value)
