#!/usr/bin/env python3
"""Слива root.yaml и clubs/*.yaml в zones/elsys.club.yaml; спира при колизия на имена."""

import sys
from pathlib import Path

import yaml


def build_zone(clubs_dir, root_file):
    zone, owner = {}, {}
    for f in [root_file, *sorted(clubs_dir.glob("*.yaml"))]:
        for name, value in (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).items():
            if name in owner:
                sys.exit(f"'{name}' е заявено и от '{owner[name]}', и от '{f.stem}' — поправи единия файл.")
            zone[name], owner[name] = value, f.stem
    return zone


if __name__ == "__main__":
    zone = build_zone(Path("clubs"), Path("root.yaml"))
    out = Path("zones/elsys.club.yaml")
    out.parent.mkdir(exist_ok=True)
    out.write_text(yaml.safe_dump(zone, sort_keys=True, allow_unicode=True), encoding="utf-8")
    print(f"Записах {len(zone)} име(на) в {out}")
