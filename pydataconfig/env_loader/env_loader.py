import dataclasses
import os

from pydataconfig.field_converter import FieldConverter
from pydataconfig.base_loader import ConfigLoader


class EnvLoader(ConfigLoader):

    def __init__(self, config, field_converter: FieldConverter):
        self.config = config
        self.field_converter = field_converter
        self.config_fields = {field.name: field for field in dataclasses.fields(config)}

    def load(self):
        for env_name, env_value in os.environ.items():
            env_name = env_name.lower()
            field = self.config_fields.get(env_name)
            if field:
                env_value = self.field_converter.get_field_converter(field)(env_value)
                setattr(self.config, env_name, env_value)
