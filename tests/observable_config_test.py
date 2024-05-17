import asyncio

from threading import Thread

import dataclasses

import unittest

from pydataconfig.observable_config import ObservableConfig


@dataclasses.dataclass
class Config(ObservableConfig):
    str_field: str = 'default_str_value'


class PyDataConfigTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.config = Config()

    def test_change_value(self):
        actual_old_value = None
        actual_new_value = None
        expected_old_value = self.config.str_field
        expected_new_value = 'new_value'

        def on_str_field_changed(old_value, new_value):
            nonlocal actual_old_value
            nonlocal actual_new_value
            actual_old_value = old_value
            actual_new_value = new_value

        self.config.on_str_field_changed += on_str_field_changed
        self.config.str_field = expected_new_value

        self.assertEqual(expected_old_value, actual_old_value)
        self.assertEqual(expected_new_value, actual_new_value)

    def test_wait(self):
        actual_old_value = None
        actual_new_value = None
        expected_old_value = self.config.str_field
        expected_new_value = 'new_value'

        def on_str_field_changed(old_value, new_value):
            nonlocal actual_old_value
            nonlocal actual_new_value
            actual_old_value = old_value
            actual_new_value = new_value

        def change_value():
            self.config.str_field = expected_new_value

        def wait():
            self.config.on_str_field_changed.wait()

        self.config.on_str_field_changed += on_str_field_changed

        wait_thread = Thread(target=wait, daemon=True)
        wait_thread.start()

        change_value_thread = Thread(target=change_value, daemon=True)
        change_value_thread.start()

        wait_thread.join()
        change_value_thread.join()

        self.assertEqual(expected_old_value, actual_old_value)
        self.assertEqual(expected_new_value, actual_new_value)

    async def test_wait_async(self):
        actual_old_value = None
        actual_new_value = None
        expected_old_value = self.config.str_field
        expected_new_value = 'new_value'

        def on_str_field_changed(old_value, new_value):
            nonlocal actual_old_value
            nonlocal actual_new_value
            actual_old_value = old_value
            actual_new_value = new_value

        async def wait():
            await self.config.on_str_field_changed

        self.config.on_str_field_changed += on_str_field_changed

        task = asyncio.create_task(wait())
        self.config.str_field = expected_new_value
        await task

        self.assertEqual(expected_old_value, actual_old_value)
        self.assertEqual(expected_new_value, actual_new_value)
