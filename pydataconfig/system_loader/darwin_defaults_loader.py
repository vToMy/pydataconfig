import dataclasses
import json
import subprocess

from pydataconfig.base_loader import ConfigLoader


class DarwinDefaultsLoader(ConfigLoader):

    def __init__(self, domain: str):
        self.domain = domain

    def load(self, config):
        config_fields = {field.name: field for field in dataclasses.fields(config)}
        defaults_config = json.loads(subprocess.check_output(f'defaults read {self.domain}'))
        for name, value in defaults_config.items():
            field = config_fields.get(name)
            if field:
                setattr(config, name, value)
