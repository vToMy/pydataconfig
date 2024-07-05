import dataclasses
import json
import subprocess

from pydataconfig.base_loader import ConfigLoader


class DarwinDefaultsLoader(ConfigLoader):

    def __init__(self, config, domain: str):
        self.config = config
        self.domain = domain
        self.config_fields = {field.name: field for field in dataclasses.fields(config)}

    def load(self):
        defaults_config = json.loads(subprocess.check_output(f'defaults read {self.domain}'))
        for name, value in defaults_config.items():
            field = self.config_fields.get(name)
            if field:
                setattr(self.config, name, value)
