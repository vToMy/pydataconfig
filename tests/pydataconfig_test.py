import dataclasses
import operator
import os
import re
import shlex
import sys
import unittest
from pathlib import Path

from pydataconfig import create_config_loader


@dataclasses.dataclass
class Config:
    str_field: str = 'default_str_value'
    int_field: int = 42
    bool_field_true: bool = True
    bool_field_false: bool = False
    path_field: Path = Path('default_path_value')
    pattern_field: re.Pattern = re.compile(r'default_patten_value')

    list_str_field: list[str] = dataclasses.field(default=lambda: ['default_str_value1', 'default_str_value2'])
    list_int_field: list[int] = dataclasses.field(default=lambda: [52, 53])
    list_bool_field: list[bool] = dataclasses.field(default=lambda: [True, False])
    list_path_field: list[Path] = dataclasses.field(default=lambda: [Path('default_path_value1'),
                                                                     Path('default_path_value2')])
    list_pattern_field: list[re.Pattern] = dataclasses.field(default=lambda: [re.compile(r'default_pattern_value1'),
                                                                              re.compile(r'default_pattern_value2')])


class PyDataConfigTest(unittest.TestCase):

    def setUp(self) -> None:
        self.config = Config()

    def test_default_value(self):
        config_loader = create_config_loader(cli=False, env=False)
        config_loader.load(self.config)
        self.assertEqual(Config.str_field, self.config.str_field)
        self.assertEqual(Config.int_field, self.config.int_field)
        self.assertEqual(Config.bool_field_true, self.config.bool_field_true)
        self.assertEqual(Config.path_field, self.config.path_field)
        self.assertEqual(Config.pattern_field, self.config.pattern_field)
        self.assertEqual(Config.list_str_field, self.config.list_str_field)
        self.assertEqual(Config.list_int_field, self.config.list_int_field)
        self.assertEqual(Config.list_bool_field, self.config.list_bool_field)
        self.assertEqual(Config.list_path_field, self.config.list_path_field)
        self.assertEqual(Config.list_pattern_field, self.config.list_pattern_field)

    def test_cli(self):
        sys.argv[1:] = shlex.split(
            '--str-field cli_str_value'
            ' --int-field 43'
            ' --bool-field-false'
            ' --no-bool-field-true'
            ' --path-field cli_path'
            ' --pattern-field cli_pattern'
            ' --list-str-field cli_str_value1 cli_str_value2'
            ' --list-int-field 54 55'
            ' --list-bool-field false true'
            ' --list-path-field cli_path_value1 cli_path_value2'
            ' --list-pattern-field cli_pattern_value1 cli_pattern_value2'
        )
        config_loader = create_config_loader()
        config_loader.load(self.config)
        self.assertEqual('cli_str_value', self.config.str_field)
        self.assertEqual(43, self.config.int_field)
        self.assertEqual(False, self.config.bool_field_true)
        self.assertEqual(True, self.config.bool_field_false)
        self.assertEqual(Path('cli_path'), self.config.path_field)
        self.assertEqual(re.compile('cli_pattern'), self.config.pattern_field)
        self.assertEqual(['cli_str_value1', 'cli_str_value2'], self.config.list_str_field)
        self.assertEqual([54, 55], self.config.list_int_field)
        self.assertEqual([False, True], self.config.list_bool_field)
        self.assertEqual([Path('cli_path_value1'), Path('cli_path_value2')], self.config.list_path_field)
        self.assertEqual([re.compile('cli_pattern_value1'), re.compile('cli_pattern_value2')],
                         self.config.list_pattern_field)

    def test_env_str(self):
        os.environ['str_field'] = 'env_str_value'
        os.environ['int_field'] = str(44)
        os.environ['bool_field_true'] = str(False)
        os.environ['bool_field_false'] = str(True)
        os.environ['path_field'] = str(Path('env_path_value'))
        os.environ['list_str_field'] = ','.join(['env_str_value1', 'env_str_value2'])
        os.environ['list_int_field'] = ','.join(map(str, [56, 57]))
        os.environ['list_bool_field'] = ','.join(map(str, [False, True]))
        os.environ['list_path_field'] = ','.join(map(str, map(Path, ['env_path_value1', 'env_path_value2'])))
        os.environ['list_pattern_field'] = ','.join(map(operator.attrgetter('pattern'),
                                                        map(re.compile, ['env_pattern_value1',
                                                                         'env_pattern_value2'])))
        config_loader = create_config_loader(cli=False)
        config_loader.load(self.config)
        self.assertEqual(os.environ['str_field'], self.config.str_field)
        self.assertEqual(int(os.environ['int_field']), self.config.int_field)
        self.assertEqual(False, self.config.bool_field_true)
        self.assertEqual(True, self.config.bool_field_false)
        self.assertEqual(Path(os.environ['path_field']), self.config.path_field)
        self.assertEqual(['env_str_value1', 'env_str_value2'], self.config.list_str_field)
        self.assertEqual([56, 57], self.config.list_int_field)
        self.assertEqual([False, True], self.config.list_bool_field)
        self.assertEqual([Path('env_path_value1'), Path('env_path_value2')], self.config.list_path_field)
        self.assertEqual([re.compile('env_pattern_value1'), re.compile('env_pattern_value2')],
                         self.config.list_pattern_field)


if __name__ == '__main__':
    unittest.main()
