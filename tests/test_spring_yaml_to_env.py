# SPDX-FileCopyrightText: 2022 Benedikt Fein
#
# SPDX-License-Identifier: EUPL-1.2

from spring_yaml_to_env.spring_yaml_to_env import flatten_yaml, parse_yaml


def test_empty_value() -> None:
    yaml = "key: # no value"
    result = flatten_yaml(parse_yaml(yaml))
    assert result == {"KEY": ""}


def test_boolean_value() -> None:
    yaml = """
    sentry.logging.enabled: true
    """
    result = flatten_yaml(parse_yaml(yaml))
    assert result == {"SENTRY_LOGGING_ENABLED": "true"}


def test_nested_yaml_values() -> None:
    yaml = """
    sentry:
        logging:
            enabled: 123.3
            other_key: "422"
    """
    result = flatten_yaml(parse_yaml(yaml))
    assert result == {
        "SENTRY_LOGGING_ENABLED": "123.3",
        "SENTRY_LOGGING_OTHERKEY": "422",
    }


def test_shortnotation_string_list() -> None:
    yaml = """
    configuration.key: [a, b, c]
    """
    result = flatten_yaml(parse_yaml(yaml))
    assert result == {"CONFIGURATION_KEY": "a, b, c"}


def test_longnotation_string_list() -> None:
    yaml = """
    configuration.key:
    - a
    - b
    - c
    """
    result = flatten_yaml(parse_yaml(yaml))
    assert result == {"CONFIGURATION_KEY": "a, b, c"}


def test_list_with_complex_objects() -> None:
    yaml = """
    key:
    - name: a
      value: b
    - name: c
      value: d
    """
    result = flatten_yaml(parse_yaml(yaml))
    assert result == {
        "KEY_0_NAME": "a",
        "KEY_0_VALUE": "b",
        "KEY_1_NAME": "c",
        "KEY_1_VALUE": "d",
    }
