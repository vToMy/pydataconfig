import dataclasses
import enum
import json
from pathlib import Path

from pydataconfig.base_loader import ConfigLoader
from pydataconfig.field_converter import FieldConverter


class ConfigType(enum.Enum):
    JSON = 'json'
    ENV = 'env'


def get_config_type_from_path(config_path: Path) -> ConfigType:
    if config_path.suffix == '.json':
        return ConfigType.JSON
    if config_path.suffix == '.env' or config_path.name == '.env':
        return ConfigType.ENV
    raise ValueError(f'Unsupported config file type: {config_path.name}')


class ConfigFileLoader(ConfigLoader):

    def __init__(self,
                 config,
                 field_converter: FieldConverter = FieldConverter(),
                 config_type: ConfigType = None,
                 config_path: Path = None,
                 encoding: str = 'utf-8'):
        self.config = config
        self.field_converter = field_converter
        if config_type is None:
            config_path = get_config_type_from_path(config_path)
        if config_type is ConfigType.JSON:
            with config_path.open('r', encoding=encoding) as config_file:
                self.config_dict = json.load(config_file)
        elif config_type is ConfigType.ENV:
            from dotenv import dotenv_values
            self.config_dict = dotenv_values(config_path, encoding=encoding)
        else:
            raise ValueError(f'Unsupported config type: {config_type}')
        self.config_fields = {field.name: field for field in dataclasses.fields(self.config)}

    def load(self):
        for env_name, env_value in self.config_dict.items():
            env_name = env_name.lower()
            field = self.config_fields.get(env_name)
            if field:
                env_value = self.field_converter.get_field_converter(field)(env_value)
                setattr(self.config, env_name, env_value)
