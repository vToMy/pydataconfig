import argparse
import dataclasses
import typing

from pydataconfig.base_loader import ConfigLoader
from pydataconfig.field_converter import FieldConverter


class CliLoader(ConfigLoader):

    def __init__(self,
                 config,
                 field_converter: FieldConverter = FieldConverter(),
                 argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()):
        self.config = config
        self.field_converter = field_converter
        self.argument_parser = argument_parser
        self.config_fields = {field.name: field for field in dataclasses.fields(self.config)}

        for field_name, field in self.config_fields.items():
            cli_arg_name = field_name.replace('_', '-')
            kwargs = {}
            if field.type is bool:
                kwargs['action'] = argparse.BooleanOptionalAction
            else:
                if typing.get_origin(field.type) is list:
                    kwargs['nargs'] = '*'
                    kwargs['type'] = self.field_converter.get_type_converter(typing.get_args(field.type)[0])
                else:
                    kwargs['type'] = self.field_converter.get_field_converter(field)
            self.argument_parser.add_argument(f'--{cli_arg_name}', **kwargs)

    def load(self):
        namespace, args = self.argument_parser.parse_known_args()
        for arg_name, arg_value in vars(namespace).items():
            if arg_name in self.config_fields:
                setattr(self.config, arg_name, arg_value)
