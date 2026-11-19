#!/usr/bin/env python3
"""Fail when a GitLab script entry does not parse as a string.

GitLab rejects a script, before_script or after_script item that is not a string or a
nested array of strings. An unquoted item containing ": " parses as a mapping, which
Yamllint accepts but GitLab lint rejects, leaving consumer pipelines with no jobs.
"""

import sys
from pathlib import Path

import yaml

SCRIPT_KEYS = ("script", "before_script", "after_script")


class Reference(list):
    """A `!reference [job, key]` tag; GitLab expands it to strings at include time."""


class Loader(yaml.SafeLoader):
    pass


Loader.add_constructor(
    "!reference",
    lambda loader, node: Reference(loader.construct_sequence(node, deep=True)),
)


def item_errors(item, where):
    if isinstance(item, (str, Reference)):
        return []
    if isinstance(item, list):
        errors = []
        for index, nested in enumerate(item):
            if not isinstance(nested, (str, Reference)):
                errors.append(f"{where}[{index}] is a {type(nested).__name__}: {nested!r}")
        return errors
    return [f"{where} is a {type(item).__name__}: {item!r}"]


def walk(node, path, errors):
    if isinstance(node, dict):
        for key, value in node.items():
            where = f"{path}.{key}" if path else str(key)
            if key in SCRIPT_KEYS and not isinstance(value, Reference):
                if isinstance(value, list):
                    for index, item in enumerate(value):
                        errors.extend(item_errors(item, f"{where}[{index}]"))
                elif not isinstance(value, str):
                    errors.append(f"{where} is a {type(value).__name__}: {value!r}")
            else:
                walk(value, where, errors)
    elif isinstance(node, list) and not isinstance(node, Reference):
        for index, value in enumerate(node):
            walk(value, f"{path}[{index}]", errors)


def main(paths):
    failures = 0
    for path in paths:
        try:
            documents = list(yaml.load_all(Path(path).read_text(), Loader=Loader))
        except yaml.YAMLError as error:
            print(f"{path}: cannot parse: {error}")
            failures += 1
            continue
        errors = []
        for document in documents:
            walk(document, "", errors)
        for error in errors:
            print(f"{path}: {error}")
        failures += len(errors)
    if failures:
        print(f"{failures} script entr{'y' if failures == 1 else 'ies'} would fail GitLab lint")
        return 1
    print(f"Checked {len(paths)} files: every script entry is a string")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
