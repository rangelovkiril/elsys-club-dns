from pathlib import Path
from textwrap import dedent

import yaml

import validate

RESERVED = {
    "exact": ["www", "mail", "admin"],
    "prefixes": ["elsys", "admin", "ns"],
}


def make_repo(tmp_path: Path, clubs: dict[str, str], reserved: dict = RESERVED) -> tuple[Path, Path]:
    clubs_dir = tmp_path / "clubs"
    clubs_dir.mkdir(parents=True)
    for name, content in clubs.items():
        (clubs_dir / f"{name}.yaml").write_text(dedent(content), encoding="utf-8")

    reserved_file = tmp_path / "reserved.yaml"
    reserved_file.write_text(yaml.safe_dump(reserved), encoding="utf-8")

    return clubs_dir, reserved_file


def run(tmp_path: Path, clubs: dict[str, str], reserved: dict = RESERVED) -> list[str]:
    clubs_dir, reserved_file = make_repo(tmp_path, clubs, reserved)
    return validate.validate(clubs_dir, reserved_file)


def test_valid_file_passes(tmp_path):
    problems = run(
        tmp_path,
        {
            "devops": """\
                devops:
                  type: CNAME
                  ttl: 3600
                  value: devops-club.github.io.
                """
        },
    )
    assert problems == []


def test_two_valid_clubs_pass_together(tmp_path):
    problems = run(
        tmp_path,
        {
            "devops": """\
                devops:
                  type: CNAME
                  value: devops-club.github.io.
                """,
            "chess": """\
                chess:
                  type: A
                  value: 1.2.3.4
                """,
        },
    )
    assert problems == []


def test_name_must_equal_or_end_with_club(tmp_path):
    problems = run(
        tmp_path,
        {
            "devops": """\
                totally-unrelated:
                  type: TXT
                  value: hello
                """
        },
    )
    assert any("трябва да е точно" in p for p in problems)


def test_subdomain_of_club_is_allowed(tmp_path):
    problems = run(
        tmp_path,
        {
            "chess": """\
                wiki.chess:
                  type: CNAME
                  value: chess.github.io.
                """
        },
    )
    assert problems == []


def test_maintainer_only_type_rejected(tmp_path):
    problems = run(
        tmp_path,
        {
            "chess": """\
                chess:
                  type: MX
                  value: mail.example.com.
                """
        },
    )
    assert any("само за maintainer-а" in p for p in problems)


def test_unknown_type_rejected(tmp_path):
    problems = run(
        tmp_path,
        {
            "chess": """\
                chess:
                  type: URLFWD
                  value: https://example.com
                """
        },
    )
    assert any("непознат тип" in p for p in problems)


def test_club_allowed_types_pass(tmp_path):
    for rtype, value in [("A", "1.2.3.4"), ("AAAA", "::1"), ("CNAME", "x.github.io."), ("TXT", "hi")]:
        problems = run(
            tmp_path / rtype,
            {"chess": f"chess:\n  type: {rtype}\n  value: {value}\n"},
        )
        assert problems == [], f"{rtype} трябваше да мине, но: {problems}"


def test_reserved_exact_name_blocked(tmp_path):
    problems = run(
        tmp_path,
        {
            "robotics": """\
                mail.robotics:
                  type: TXT
                  value: fake
                """
        },
        reserved={"exact": ["mail.robotics"], "prefixes": []},
    )
    assert any("запазено име" in p for p in problems)


def test_reserved_prefix_name_blocked(tmp_path):
    problems = run(
        tmp_path,
        {
            "ns": """\
                ns:
                  type: A
                  value: 1.2.3.4
                """
        },
    )
    assert any("запазен" in p for p in problems)


def test_club_name_itself_reserved(tmp_path):
    problems = run(
        tmp_path,
        {
            "admin": """\
                foo.admin:
                  type: TXT
                  value: hi
                """
        },
    )
    assert any("името на клуба 'admin'" in p for p in problems)


def test_malformed_yaml_gives_friendly_message(tmp_path):
    problems = run(
        tmp_path,
        {
            "broken": "devops: [this is not: valid yaml"
        },
    )
    assert len(problems) == 1
    assert "YAML" in problems[0]
    assert "Traceback" not in problems[0]


def test_record_without_type_field_gives_friendly_message(tmp_path):
    problems = run(
        tmp_path,
        {
            "chess": """\
                chess:
                  ttl: 3600
                  value: 1.2.3.4
                """
        },
    )
    assert any("няма поле 'type'" in p for p in problems)
