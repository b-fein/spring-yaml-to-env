# SPDX-FileCopyrightText: 2022 Benedikt Fein
#
# SPDX-License-Identifier: EUPL-1.2

import textwrap
from pathlib import Path

from _pytest.capture import CaptureFixture

from spring_yaml_to_env.spring_yaml_to_env import argument_parser, main


def test_parse_simple_file(capsys: CaptureFixture[str]) -> None:
    main([Path("tests/fixtures/simple_file.yaml")], sort=False)

    captured = capsys.readouterr()
    assert captured.out == textwrap.dedent(
        """\
        CONFIG_SINGLEVALUE="12"
        CONFIG_KEY="item1, item2, item3"
        """
    )


def test_parse_simple_file_sorting(capsys: CaptureFixture[str]) -> None:
    main([Path("tests/fixtures/simple_file.yaml")], sort=True)

    captured = capsys.readouterr()
    assert captured.out == textwrap.dedent(
        """\
        CONFIG_KEY="item1, item2, item3"
        CONFIG_SINGLEVALUE="12"
        """
    )


def test_parse_empty_value(capsys: CaptureFixture[str]) -> None:
    main([Path("tests/fixtures/empty_value.yaml")], sort=True)

    captured = capsys.readouterr()
    assert captured.out == """CONFIG_KEY=""\n"""


def test_argparser_single_file() -> None:
    files = ["some_file.yaml"]
    args = argument_parser().parse_args(files)
    assert args.yaml_files == [Path(f) for f in files]
    assert not args.sort


def test_argparser_multiple_files() -> None:
    files = ["some_file.yaml", "other_file.yaml"]
    args = argument_parser().parse_args(["-s", *files])
    assert args.yaml_files == [Path(f) for f in files]
    assert args.sort
