from typing import Callable, Any, Awaitable, Generator, Self

import re

import inspect

import threading
import asyncio


type CallbackType[**P] = Callable[P, Any] | Callable[P, Awaitable[Any]]
type TimeoutType = int | float


def get_running_loop() -> asyncio.AbstractEventLoop | None:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return None


class Event[**P]:
    def __init__(self):
        self.sync_callbacks: list[Callable[P, Any]] = []
        self.async_callbacks: list[Callable[P, Awaitable[Any]]] = []
        self.thread_condition = threading.Condition()
        self.asyncio_condition = asyncio.Condition()

        self.state_lock = threading.Lock()
        self.async_state_lock = asyncio.Lock()
        self.last_args: P.args = None
        self.last_kwargs: P.kwargs = None
        self.async_callbacks_tasks: list[asyncio.Task] = []

    def add_callback(self, callback: CallbackType[P]) -> None:
        if inspect.iscoroutinefunction(callback):
            self.async_callbacks.append(callback)
        else:
            self.sync_callbacks.append(callback)

    def remove_callback(self, callback: CallbackType[P]) -> None:
        if inspect.iscoroutinefunction(callback):
            self.async_callbacks.remove(callback)
        else:
            self.sync_callbacks.remove(callback)

    def __iadd__(self, callback: CallbackType[P]) -> Self:
        self.add_callback(callback)
        return self

    def __isub__(self, callback: CallbackType[P]) -> Self:
        self.remove_callback(callback)
        return self

    def emit(self, *args: P.args, **kwargs: P.kwargs) -> None:
        with self.state_lock:
            self.last_args = args
            self.last_kwargs = kwargs
        for callback in self.sync_callbacks:
            callback(*args, **kwargs)
        self.set()

    async def async_emit(self, *args: P.args, **kwargs: P.kwargs) -> None:
        async with self.async_state_lock:
            self.last_args = args
            self.last_kwargs = kwargs
            self.async_callbacks_tasks = []
        for async_callback in self.async_callbacks:
            self.async_callbacks_tasks.append(asyncio.create_task(async_callback(*args, **kwargs)))
        await self.set_async()

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.emit(*args, **kwargs)
        if get_running_loop():
            asyncio.create_task(self.async_emit(*args, **kwargs))

    def wait(self, timeout: TimeoutType = None) -> tuple[P.args, P.kwargs]:
        with self.state_lock:
            last_args, last_kwargs = self.last_args, self.last_kwargs
        with self.thread_condition:
            self.thread_condition.wait(timeout)
        return last_args, last_kwargs

    async def wait_async(self, wait_for_async_callbacks_tasks: bool = False) -> tuple[P.args, P.kwargs]:
        async with self.async_state_lock:
            last_args, last_kwargs, async_callbacks_tasks = self.last_args, self.last_kwargs, self.async_callbacks_tasks
        async with self.asyncio_condition:
            await self.asyncio_condition.wait()
        if wait_for_async_callbacks_tasks and async_callbacks_tasks:
            await asyncio.gather(*async_callbacks_tasks)
        return last_args, last_kwargs

    def __await__(self) -> Generator[Any, None, tuple[P.args, P.kwargs]]:
        return self.wait_async().__await__()

    def set(self) -> None:
        with self.thread_condition:
            self.thread_condition.notify_all()

    async def set_async(self):
        async with self.asyncio_condition:
            self.asyncio_condition.notify_all()


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
