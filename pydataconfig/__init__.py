import platform
from pathlib import Path

from pydataconfig.base_loader import ConfigLoader
from pydataconfig.cli_loader.cli_loader import CliLoader
from pydataconfig.composite_loader import CompositeLoader
from pydataconfig.config_file_loader.config_file_loader import ConfigFileLoader, ConfigType
from pydataconfig.env_loader.env_loader import EnvLoader
from pydataconfig.field_converter import FieldConverter


def create_config_loader(
        config,
        field_converter: FieldConverter = FieldConverter(),
        cli: bool = True,
        dot_env: bool = False, env: bool = True,
        config_path: Path = None,
        system_global: bool = False, system_user: bool = False,
        domain: str = None, company_name: str = None, product_name: str = None) -> ConfigLoader:
    config_loaders = []
    if system_global or system_user:
        if platform.system() == 'Darwin':
            if not domain:
                raise ValueError('Missing required parameter for darwin system loader: `domain`')
            from pydataconfig.system_loader.darwin_defaults_loader import DarwinDefaultsLoader
            config_loaders.append(DarwinDefaultsLoader(config, domain))
        elif platform.system() == 'Windows':
            if not company_name or not product_name:
                raise ValueError('Missing one or more required parameters for windows system loader:'
                                 ' `company_name` and `product_name`')
            from pydataconfig.system_loader.windows_registry_loader import WindowsRegistryLoader
            from pydataconfig.system_loader.windows_registry_loader import SystemConfigType
            if system_global:
                config_loaders.append(WindowsRegistryLoader(config,
                                                            company_name=company_name, product_name=product_name,
                                                            system_config_type=SystemConfigType.GLOBAL))
            if system_user:
                config_loaders.append(WindowsRegistryLoader(config,
                                                            company_name=company_name, product_name=product_name,
                                                            system_config_type=SystemConfigType.USER))
    if config_path is not None:
        config_loaders.append(ConfigFileLoader(config,
                                               field_converter=field_converter, config_type=ConfigType.JSON,
                                               config_path=config_path))
    if dot_env:
        config_loaders.append(ConfigFileLoader(config,
                                               field_converter=field_converter, config_type=ConfigType.ENV))
    if env:
        config_loaders.append(EnvLoader(config, field_converter=field_converter))
    if cli:
        config_loaders.append(CliLoader(config, field_converter=field_converter))
    if len(config_loaders) == 1:
        return config_loaders[0]
    return CompositeLoader(config_loaders)
