import dataclasses

import winreg

from pydataconfig.base_loader import ConfigLoader
from pydataconfig.system_loader import SystemConfigType


class WindowsRegistryLoader(ConfigLoader):

    def __init__(self, config, company_name: str, product_name: str, system_config_type: SystemConfigType):
        self.config = config
        self.company_name = company_name
        self.product_name = product_name
        self.system_config_type = system_config_type
        self.config_fields = {field.name: field for field in dataclasses.fields(self.config)}

    def load(self):
        if self.system_config_type is SystemConfigType.GLOBAL:
            key = winreg.HKEY_LOCAL_MACHINE
            software = 'SOFTWARE'
        elif self.system_config_type is SystemConfigType.USER:
            key = winreg.HKEY_CURRENT_USER
            software = 'Software'
        else:
            raise Exception(self.system_config_type)

        sub_key = rf'{software}\{self.company_name}\{self.product_name}'
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as key_handle:
            for i in range(winreg.QueryInfoKey(key_handle)[1]):
                name, value, value_type = winreg.EnumValue(key_handle, i)
                field = self.config_fields.get(name)
                if field:
                    setattr(self.config, name, value)
