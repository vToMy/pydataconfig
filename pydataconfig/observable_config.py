import re

import inspect

import threading
import asyncio


class Event:
    def __init__(self):
        self.sync_callbacks = []
        self.async_callbacks = []
        self.thread_condition = threading.Event()
        self.asyncio_condition = asyncio.Event()
        self.last_args = None
        self.last_kwargs = None

    def __call__(self, *args, **kwargs):
        self.clear()
        for callback in self.sync_callbacks:
            callback(*args, **kwargs)
        for callback in self.async_callbacks:
            asyncio.get_running_loop().run_until_complete(callback(*args, **kwargs))
        self.last_args = args
        self.last_kwargs = kwargs
        self.set()

    def __iadd__(self, callback):
        if inspect.iscoroutinefunction(callback):
            self.async_callbacks.append(callback)
        else:
            self.sync_callbacks.append(callback)
        return self

    def __isub__(self, callback):
        if inspect.iscoroutinefunction(callback):
            self.async_callbacks.remove(callback)
        else:
            self.sync_callbacks.remove(callback)
        return self

    def __await__(self):
        return self.wait_async().__await__()

    async def wait_async(self):
        await self.asyncio_condition.wait()
        return self.last_args, self.last_kwargs

    def wait(self, timeout=None):
        self.thread_condition.wait(timeout)
        return self.last_args, self.last_kwargs

    def set(self):
        self.thread_condition.set()
        self.asyncio_condition.set()

    def clear(self):
        self.thread_condition.clear()
        self.asyncio_condition.clear()


class ObservableConfig:
    def __getattr__(self, item):
        match = re.match(r'on_(.+)_changed', item)
        if match:
            key = match.group(1)
            if not hasattr(self, key):
                raise AttributeError(f'No field called: {key} found for: {item}')
            event = Event()
            super().__setattr__(item, event)
            return event
        raise AttributeError(item)

    def __setattr__(self, key, value):
        previous_value = getattr(self, key)
        super().__setattr__(key, value)
        if value != previous_value:
            event = getattr(self, f'on_{key}_changed', None)
            if isinstance(event, Event):
                event(previous_value, value)
