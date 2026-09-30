#!/usr/bin/env python3
"""Политики за clubs/*.yaml. Структурата на записите я проверява octodns-validate."""

import sys
from pathlib import Path

import yaml

ALLOWED = ["A", "AAAA", "CNAME", "TXT"]
MAINTAINER_ONLY = ["NS", "MX", "CAA"]


def reserved_reason(name, reserved):
    if name in reserved["exact"]:
        return "е запазено име"
    for prefix in reserved["prefixes"]:
        if name == prefix or name.endswith(f".{prefix}"):
            return f"е под запазения префикс '{prefix}'"


def check_file(path, reserved):
    club = path.stem
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [f"{path.name}: невалиден YAML: {e}"]
    if not isinstance(data, dict):
        return [f"{path.name}: файлът трябва да е речник от вида 'име: запис'"]

    errors = []
    if why := reserved_reason(club, reserved):
        errors.append(f"{path.name}: името на клуба '{club}' {why} — преименувай файла")

    for name, value in data.items():
        name = str(name)
        if not (name == club or name.endswith(f".{club}")):
            errors.append(f"{path.name}: '{name}' трябва да е точно '{club}' или да завършва на '.{club}'")
        if why := reserved_reason(name, reserved):
            errors.append(f"{path.name}: '{name}' {why} и не може да се заявява от клуб")
        for rec in value if isinstance(value, list) else [value]:
            rtype = rec.get("type") if isinstance(rec, dict) else None
            if rtype is None:
                errors.append(f"{path.name}: записът за '{name}' няма поле 'type'")
            elif rtype in MAINTAINER_ONLY:
                errors.append(f"{path.name}: типът {rtype} за '{name}' е само за maintainer-а (позволени: {', '.join(ALLOWED)})")
            elif rtype not in ALLOWED:
                errors.append(f"{path.name}: непознат тип {rtype} за '{name}' (позволени: {', '.join(ALLOWED)})")
    return errors


def validate(clubs_dir, reserved_file):
    raw = yaml.safe_load(reserved_file.read_text(encoding="utf-8")) or {}
    reserved = {"exact": set(raw.get("exact") or []), "prefixes": raw.get("prefixes") or []}
    return [e for f in sorted(clubs_dir.glob("*.yaml")) for e in check_file(f, reserved)]


if __name__ == "__main__":
    errors = validate(Path("clubs"), Path("reserved.yaml"))
    for e in errors:
        print(f"✗ {e}")
    sys.exit(1 if errors else 0)
