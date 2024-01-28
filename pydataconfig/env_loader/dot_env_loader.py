import dataclasses
from pathlib import Path

from dotenv import dotenv_values

from pydataconfig.field_converter import FieldConverter
from pydataconfig.base_loader import ConfigLoader


class DotEnvLoader(ConfigLoader):

    def __init__(self, field_converter: FieldConverter, dot_env_path: Path = None):
        self.dot_env_path = dot_env_path
        self.field_converter = field_converter

    def load(self, config):
        config_fields = {field.name: field for field in dataclasses.fields(config)}
        for env_name, env_value in dotenv_values(self.dot_env_path).items():
            env_name = env_name.lower()
            field = config_fields.get(env_name)
            if field:
                env_value = self.field_converter.get_field_converter(field)(env_value)
                setattr(config, env_name, env_value)
