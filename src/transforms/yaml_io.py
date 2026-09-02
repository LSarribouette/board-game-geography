from __future__ import annotations

from pathlib import Path

import yaml


class QuotedStringDumper(yaml.SafeDumper):
    pass


def quoted_string(dumper: yaml.Dumper, value: str) -> yaml.ScalarNode:
    # Force quotes on every string so numeric-looking keys stay strings.
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="'")


QuotedStringDumper.add_representer(str, quoted_string)


def read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_yaml(data: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(
            data,
            handle,
            Dumper=QuotedStringDumper,
            allow_unicode=True,
            sort_keys=False,
        )
