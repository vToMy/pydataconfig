# pydataconfig

```python
import pydataconfig
import dataclasses

@dataclasses.dataclass
class Config:
  str_field: str

config_loader = create_config_loader.create_config_loader(
  cli=True,
  dot_env=True,
  env=True,
  system_global=True,
  system_user=True,
  domain='com.company.product',
  company_name='Company',
  product_name='Product')

config = Config()
config_loader.load_config(config)
```

Load app external configuration into a `dataclass` easily.
Config will be populated according to the following precendence:
1. System config
   * Windows: `/HKEY_LOCAL_MACHINE/SOFTWARE/Company/Product/str_field`
2. User config
   * Windows: `/HKEY_CURRENT_USER/SOFTWARE/Company/Product/str_field`
   * Mac: `defaults read com.company.product str_field`
3. dot-env: `.env`: `STR_FIELD=VALUE`
4. Environment variables: `STR_FIELD=VALUE`
5. CLI: `--str-field value`
