#! /usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Benedikt Fein
#
# SPDX-License-Identifier: EUPL-1.2

"""
Script to convert Spring configuration YAML files into their environment
variable representation.
"""

import logging
from argparse import ArgumentParser
from functools import reduce
from pathlib import Path
from typing import Any

import yaml


def to_spring_env_property(config_option: str) -> str:
    """
    Converts YAML keys to environment variable names.

    The keys of configuration values are converted by removing underscores and
    dashes, and making all letters uppercase.

    :param config_option: The key of the config option that should be converted.
    :return: The key as environment variable name.
    """
    replacements = [("_", ""), ("-", ""), (".", "_")]

    def replace(option: str, replacement: tuple[str, str]) -> str:
        replace_from, replace_to = replacement
        return option.replace(replace_from, replace_to)

    return reduce(replace, replacements, config_option).upper()


def path_to_spring_env_property(path: list[str]) -> str:
    """
    Flattens the path of a configuration option key into a single environment
    variable name.

    In YAML those paths are either denoted by ``some.configuration.key`` or by
    indentation::

        some:
            configuration:
                key: ...

    :param path: The complete path of a configuration key.
    :return: The key as environment variable name.
    """
    return "_".join(map(to_spring_env_property, path))


def save_value(result: dict[str, str], option_name: list[str], value: str) -> None:
    """
    Adds the given config entry to the result.

    :param result: The dictionary holding the key-value-pairs of environment variables.
    :param option_name: The key of the config entry as YAML path.
    :param value: The value of the config entry.
    """
    result[path_to_spring_env_property(option_name)] = value


def flatten_list(
    yml: list[Any], current_path: list[str] | None = None
) -> dict[str, str]:
    """
    Converts a YAML list of configuration options into their environment
    variable representation.

    :param yml: The YAML list of configuration values.
    :param current_path: The path within the configuration that points to the list.
    :return: All list items recursively resolved as environment variable
             key-value-pairs.
    """

    def is_str_list(items: list[Any]) -> bool:
        return all(isinstance(i, str) for i in items)

    if current_path is None:
        current_path = []

    result: dict[str, str] = {}

    if is_str_list(yml):
        # String lists can be given in the yaml as
        # or
        # key:
        # - a
        # - b
        # Both are converted to `"KEY": "a, b"`
        save_value(result, current_path, ", ".join(yml))
    else:
        # The list contains complex objects, e.g.
        # key:
        # - ...
        # In this case the index of the complex object in the list turns into a part of
        # the key:
        for idx, item in enumerate(yml):
            path = [*current_path, str(idx)]
            assert isinstance(  # noqa: S101, yaml can only be either list or dict
                item, dict
            )
            result.update(flatten_yaml(item, path))

    return result


def flatten_yaml(
    yml: dict[str, Any], current_path: list[str] | None = None
) -> dict[str, str]:
    """
    Flattens a YAML file into key-value pairs by recursively walking over all elements.

    :param yml: The YAML data that should be converted.
    :param current_path: The path of keys within the YAML leading up to the root of
                         ``yml``.
    :return: A map of key-value-pairs obtained from the YAML. The keys are in the format
             that is used by Spring to read the values from environment variables.
    """
    if current_path is None:
        current_path = []

    result: dict[str, str] = {}

    for k, v in yml.items():
        path = [*current_path, k]

        match v:
            case dict(value):
                result.update(flatten_yaml(value, path))
            case list(value):
                result.update(flatten_list(value, path))
            case bool(value):
                save_value(result, path, str(value).lower())
            case float(value) | int(value) | str(value):
                save_value(result, path, str(value))
            case None:
                save_value(result, path, "")
            case _:
                logging.warning("Unknown YAML element: path=%s, value=%s", path, v)

    return result


def parse_yaml(yaml_src: str) -> dict[str, Any]:
    """
    Parses some YAML structure.

    :param yaml_src: The YAML source.
    :return: The parsed YAML.
    :raises TypeError: In case the YAML contains multiple documents or consists
        of a list of values instead of a configuration with key-value pairs.
    """
    result = yaml.full_load(yaml_src)
    if not isinstance(result, dict):
        message = (
            "Expected a YAML file that contains a single document with a "
            "Spring configuration."
        )
        raise TypeError(message)

    return result


def flatten_yaml_file(filename: Path) -> dict[str, str]:
    """
    Converts a single YAML file into the environment variable key-value-mappings.

    :param filename: The file that should be converted.
    :return: The mapping of environment variables to their values.
    """
    with filename.open(encoding="UTF-8") as file:
        file_content: str = file.read()
        parsed_yaml = parse_yaml(file_content)
        return flatten_yaml(parsed_yaml)


def main(files: list[Path], *, sort: bool = False) -> None:
    """
    Main entry point to the script.

    :param files: The list of YAML files that should be converted.
    :param sort: True, if the config keys should be sorted lexicographically.
    """
    result: dict[str, str] = {}

    for file in files:
        result.update(flatten_yaml_file(file))

    keys = list(result.keys())
    if sort:
        keys = sorted(keys)

    for key in keys:
        print(f'{key}="{result[key]}"')


def argument_parser() -> ArgumentParser:
    """
    Builds the argument parser.

    :return: The argument parser.
    """
    description = (
        "Converts a list of Spring configuration YAML files into a combined list of "
        "environment variable mappings. "
        "The conversions of all files are combined and printed on the standard output "
        "in the format as required by .env-Files, i.e, one 'KEY=VALUE' entry per line."
    )
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-s",
        "--sort",
        dest="sort",
        action="store_true",
        help="sort config options lexicographically",
        default=False,
    )
    parser.add_argument(
        "yaml_files", nargs="*", help="YAML files that should be converted", type=Path
    )
    return parser


if __name__ == "__main__":
    args = argument_parser().parse_args()
    main(args.yaml_files, sort=args.sort)
