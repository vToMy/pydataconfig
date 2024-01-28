import platform
import warnings

from pydataconfig.base_loader import ConfigLoader
from pydataconfig.cli_loader.cli_loader import CliLoader
from pydataconfig.composite_loader import CompositeLoader
from pydataconfig.env_loader.env_loader import EnvLoader
from pydataconfig.field_converter import FieldConverter


def create_config_loader(cli: bool = True,
                         dot_env: bool = False, env: bool = True,
                         system_global: bool = False, system_user: bool = False,
                         domain: str = None, company_name: str = None, product_name: str = None) -> CompositeLoader:
    config_loaders = []
    field_converter = FieldConverter()
    if system_global or system_user:
        if platform.system() == 'Darwin':
            if not domain:
                raise ValueError('Missing required parameter for darwin system loader: `domain`')
            from pydataconfig.system_loader.darwin_defaults_loader import DarwinDefaultsLoader
            config_loaders.append(DarwinDefaultsLoader(domain))
        elif platform.system() == 'Windows':
            if not company_name or not product_name:
                raise ValueError('Missing one or more required parameters for windows system loader:'
                                 ' `company_name` and `product_name`')
            from pydataconfig.system_loader.windows_registry_loader import WindowsRegistryLoader
            from pydataconfig.system_loader.windows_registry_loader import SystemConfigType
            if system_global:
                config_loaders.append(WindowsRegistryLoader(company_name=company_name, product_name=product_name,
                                                            system_config_type=SystemConfigType.GLOBAL))
            if system_user:
                config_loaders.append(WindowsRegistryLoader(company_name=company_name, product_name=product_name,
                                                            system_config_type=SystemConfigType.USER))
    if dot_env:
        try:
            from pydataconfig.env_loader.dot_env_loader import DotEnvLoader
            config_loaders.append(DotEnvLoader(field_converter=field_converter))
        except ImportError:
            warnings.warn('`python-dotenv` package must be installed to use `dot_env`')
    if env:
        config_loaders.append(EnvLoader(field_converter=field_converter))
    if cli:
        config_loaders.append(CliLoader(field_converter=field_converter))
    return CompositeLoader(config_loaders)
