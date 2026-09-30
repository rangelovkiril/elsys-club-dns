from pathlib import Path

import pytest

import build_zone


def make_clubs(tmp_path: Path, clubs: dict[str, str]) -> Path:
    clubs_dir = tmp_path / "clubs"
    clubs_dir.mkdir()
    for name, content in clubs.items():
        (clubs_dir / f"{name}.yaml").write_text(content, encoding="utf-8")
    return clubs_dir


def test_merges_multiple_clubs(tmp_path):
    clubs_dir = make_clubs(
        tmp_path,
        {
            "devops": "devops:\n  type: CNAME\n  value: a.github.io.\n",
            "chess": "chess:\n  type: A\n  value: 1.2.3.4\n",
        },
    )
    zone = build_zone.build_zone(clubs_dir)
    assert set(zone.keys()) == {"devops", "chess"}


def test_collision_between_clubs_raises(tmp_path):
    clubs_dir = make_clubs(
        tmp_path,
        {
            "devops": "shared.devops:\n  type: TXT\n  value: x\n",
            "other": "shared.devops:\n  type: TXT\n  value: y\n",
        },
    )

    with pytest.raises(SystemExit) as exc_info:
        build_zone.build_zone(clubs_dir)

    message = str(exc_info.value)
    assert "shared.devops" in message
    assert "devops" in message and "other" in message
