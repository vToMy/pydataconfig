import dataclasses
import json
import subprocess

from pydataconfig.base_loader import ConfigLoader
from pydataconfig.system_loader import SystemConfigType


class DarwinDefaultsLoader(ConfigLoader):

    def __init__(self, config, domain: str, system_config_type: SystemConfigType):
        self.config = config
        self.domain = domain
        self.system_config_type = system_config_type
        self.config_fields = {field.name: field for field in dataclasses.fields(config)}

    def load(self):
        if self.system_config_type is SystemConfigType.GLOBAL:
            domain = f'/Library/Preferences/{self.domain}'
        elif self.system_config_type is SystemConfigType.USER:
            domain = self.domain
        else:
            raise Exception(self.system_config_type)
        defaults_config = json.loads(subprocess.check_output(f'defaults read {domain}'))
        for name, value in defaults_config.items():
            field = self.config_fields.get(name)
            if field:
                setattr(self.config, name, value)
