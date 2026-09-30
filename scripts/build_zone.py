#!/usr/bin/env python3
"""Слива clubs/*.yaml в zones/elsys.club.yaml (формат на OctoDNS).

Всеки файл в clubs/ е речник от вида {име: запис/и}, точно както очаква
octodns.provider.yaml.YamlProvider за цялата зона. Скриптът просто ги
събира в един речник и го записва. Без валидация — тя идва в Етап 4.
"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLUBS_DIR = ROOT / "clubs"
ZONE_FILE = ROOT / "zones" / "elsys.club.yaml"


def build_zone() -> dict:
    zone: dict = {}
    for club_file in sorted(CLUBS_DIR.glob("*.yaml")):
        data = yaml.safe_load(club_file.read_text(encoding="utf-8")) or {}
        zone.update(data)
    return zone


def main() -> None:
    zone = build_zone()
    ZONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ZONE_FILE.write_text(
        yaml.safe_dump(zone, default_flow_style=False, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Записах {len(zone)} име(на) в {ZONE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
