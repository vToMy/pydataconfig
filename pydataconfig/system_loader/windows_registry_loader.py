import dataclasses
import enum
import winreg

from pydataconfig.base_loader import ConfigLoader


class SystemConfigType(enum.Enum):
    GLOBAL = enum.auto()
    USER = enum.auto()


class WindowsRegistryLoader(ConfigLoader):

    def __init__(self, company_name: str, product_name: str, system_config_type: SystemConfigType):
        self.company_name = company_name
        self.product_name = product_name
        self.system_config_type = system_config_type

    def load(self, config):
        config_fields = {field.name: field for field in dataclasses.fields(config)}
        if self.system_config_type is SystemConfigType.GLOBAL:
            key = winreg.HKEY_LOCAL_MACHINE
        elif self.system_config_type is SystemConfigType.USER:
            key = winreg.HKEY_CURRENT_USER
        else:
            raise Exception(self.system_config_type)

        sub_key = rf'Software\{self.company_name}\{self.product_name}'
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as key_handle:
            for i in range(winreg.QueryInfoKey(key_handle)[1]):
                name, value, value_type = winreg.EnumValue(key_handle, i)
                field = config_fields.get(name)
                if field:
                    setattr(config, name, value)
