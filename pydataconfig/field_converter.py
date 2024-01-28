import csv
import dataclasses
import re
import typing


class FieldConverter:
    def __init__(self, **csv_reader_kwargs):
        self.csv_reader_kwargs = csv_reader_kwargs
        self.field_type_to_conversion = {
            re.Pattern: lambda value: re.compile(value),
            bool: lambda value: value if isinstance(value, bool) else value.lower() == 'true'
        }

    def get_type_converter(self, type_):
        return self.field_type_to_conversion.get(type_, type_)

    def get_field_converter(self, field: dataclasses.Field):
        if typing.get_origin(field.type) is list:
            item_type = typing.get_args(field.type)[0]
            item_converter = self.get_type_converter(item_type)
            return self.list_converter(item_converter)

        return self.get_type_converter(field.type)

    def list_converter(self, item_converter):
        def inner(value):
            return list(map(item_converter, self.convert_line(value)))
        return inner

    def convert_line(self, line: str) -> list[str]:
        return next(csv.reader([line], **self.csv_reader_kwargs))
