import dataclasses
import json
from pathlib import Path
from typing import Literal

from pydataconfig.field_converter import FieldConverter
from pydataconfig.base_loader import ConfigLoader


def get_config_type_from_path(config_path: Path) -> str:
    if config_path.suffix == 'json':
        return 'json'
    if config_path.suffix == '.env' or config_path.name == '.env':
        return '.env'
    raise ValueError(f'Unsupported config file type: {config_path.name}')


class ConfigFileLoader(ConfigLoader):

    def __init__(self, field_converter: FieldConverter,
                 config_type: Literal['json', '.env'] = None,
                 config_path: Path = None,
                 encoding: str = 'utf-8'):
        self.field_converter = field_converter
        if config_type is None:
            config_path = get_config_type_from_path(config_path)
        if config_type == 'json':
            with config_path.open('r', encoding=encoding) as config_file:
                self.config_dict = json.load(config_file)
        elif config_type == '.env':
            from dotenv import dotenv_values
            self.config_dict = dotenv_values(config_path, encoding=encoding)
        else:
            raise ValueError(f'Unsupported config type: {config_type}')

    def load(self, config):
        config_fields = {field.name: field for field in dataclasses.fields(config)}
        for env_name, env_value in self.config_dict.items():
            env_name = env_name.lower()
            field = config_fields.get(env_name)
            if field:
                env_value = self.field_converter.get_field_converter(field)(env_value)
                setattr(config, env_name, env_value)
