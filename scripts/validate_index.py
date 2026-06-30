from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
INDEX = ROOT / "index"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    json.loads((ROOT / "schemas/dataset-reference.schema.json").read_text())
    records = []
    for path in sorted(DATASETS.rglob("*.yml")):
        record = load_simple_yaml(path)
        errors.extend(validate(path, record))
        records.append((path, record))
    errors.extend(validate_no_conflicts(records))

    manifests = render_manifests(records)
    if args.write_manifest:
        write_manifests(manifests)
    else:
        errors.extend(validate_manifests(manifests))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"validated {len(records)} dataset reference(s)")
    return 0


def load_simple_yaml(path: Path) -> dict[str, object]:
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]
    for line_number, raw in enumerate(path.read_text().splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ValueError(f"{path}:{line_number}: indentation must use two spaces")
        if ":" not in raw:
            raise ValueError(f"{path}:{line_number}: expected `key: value`")
        key, value = raw.strip().split(":", 1)
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        parsed = parse_value(value.strip())
        parent[key] = parsed
        if parsed == {}:
            stack.append((indent, parsed))
    return root


def parse_value(value: str) -> object:
    if value == "":
        return {}
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if re.fullmatch(r"[0-9]+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [item.strip() for item in inner.split(",")]
    return value.strip("\"'")


def validate(path: Path, record: dict[str, object]) -> list[str]:
    errors: list[str] = []
    required = [
        "dataset_id",
        "title",
        "source_url",
        "source_domain",
        "source_type",
        "update_frequency",
        "license",
    ]
    for key in required:
        if key not in record:
            errors.append(f"{path}: missing `{key}`")
    for key in ["storage", "review", "notes", "crawl"]:
        if key in record:
            errors.append(f"{path}: `{key}` is not allowed in dataset YAML")

    dataset_id = str(record.get("dataset_id", ""))
    source_domain = str(record.get("source_domain", ""))
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*[a-z0-9]", dataset_id):
        errors.append(f"{path}: dataset_id must be lowercase slug")
    if source_domain and f"/by-domain/{source_domain}/" not in path.as_posix():
        errors.append(f"{path}: path must include /by-domain/{source_domain}/")
    if not is_url(str(record.get("source_url", ""))):
        errors.append(f"{path}: source_url must be an http(s) URL")
    if record.get("source_type") not in {"api", "rss", "html_page", "file", "mixed"}:
        errors.append(f"{path}: unsupported source_type")
    if record.get("update_frequency") not in {
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "yearly",
        "adhoc",
    }:
        errors.append(f"{path}: unsupported update_frequency")

    license_info = expect_map(path, record, "license", errors)
    if not license_info.get("name"):
        errors.append(f"{path}: license.name is required")
    if not is_url(str(license_info.get("url", ""))):
        errors.append(f"{path}: license.url must be an http(s) URL")
    if "redistribution_allowed" in license_info:
        errors.append(f"{path}: license.redistribution_allowed is not allowed")

    return errors


def validate_no_conflicts(records: list[tuple[Path, dict[str, object]]]) -> list[str]:
    errors: list[str] = []
    seen_dataset_ids: dict[str, Path] = {}
    seen_source_urls: dict[str, Path] = {}
    seen_r2_prefixes: dict[str, Path] = {}
    for path, record in records:
        dataset_id = str(record.get("dataset_id", ""))
        source_url = str(record.get("source_url", ""))
        source_domain = str(record.get("source_domain", ""))
        r2_prefix = expected_r2_prefix(source_domain, dataset_id)
        for label, value, seen in [
            ("dataset_id", dataset_id, seen_dataset_ids),
            ("source_url", source_url, seen_source_urls),
            ("derived r2_prefix", r2_prefix, seen_r2_prefixes),
        ]:
            if value in seen:
                errors.append(f"{path}: duplicate {label} also used by {seen[value]}")
            else:
                seen[value] = path
    return errors


def expect_map(
    path: Path, record: dict[str, object], key: str, errors: list[str]
) -> dict[str, object]:
    value = record.get(key)
    if isinstance(value, dict):
        return value
    errors.append(f"{path}: `{key}` must be a map")
    return {}


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def expected_r2_prefix(source_domain: str, dataset_id: str) -> str:
    return f"catalog/by-domain/{source_domain}/{r2_shard(dataset_id)}/{dataset_id}"


def r2_shard(dataset_id: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "", dataset_id.lower())
    return (clean[:2] or "xx").ljust(2, "x")


def write_manifests(manifests: dict[Path, str]) -> None:
    for old in INDEX.rglob("*.yml"):
        if old not in manifests:
            old.unlink()
    for path, text in manifests.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def validate_manifests(manifests: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    existing = set(INDEX.rglob("*.yml")) if INDEX.exists() else set()
    expected = set(manifests)
    for path in sorted(expected - existing):
        errors.append(f"{path.relative_to(ROOT)} is missing; run `make manifest`")
    for path in sorted(existing - expected):
        errors.append(f"{path.relative_to(ROOT)} is stale; run `make manifest`")
    for path in sorted(expected & existing):
        if path.read_text() != manifests[path]:
            errors.append(f"{path.relative_to(ROOT)} is stale; run `make manifest`")
    return errors


def render_manifests(records: list[tuple[Path, dict[str, object]]]) -> dict[Path, str]:
    grouped: dict[Path, list[tuple[Path, dict[str, object]]]] = {}
    for path, record in records:
        source_domain = str(record["source_domain"])
        dataset_id = str(record["dataset_id"])
        shard = r2_shard(dataset_id)
        manifest_path = INDEX / "by-domain" / source_domain / f"{shard}.yml"
        grouped.setdefault(manifest_path, []).append((path, record))

    manifests: dict[Path, str] = {}
    for manifest_path, items in grouped.items():
        lines = ["datasets:"]
        for path, record in items:
            lines.extend(render_manifest_item(path, record))
        manifests[manifest_path] = "\n".join(lines) + "\n"
    return manifests


def render_manifest_item(path: Path, record: dict[str, object]) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    return [
        f"  - dataset_id: {record['dataset_id']}",
        f"    path: {rel}",
        f"    title: {record['title']}",
        f"    source_domain: {record['source_domain']}",
        "    r2_prefix: "
        f"{expected_r2_prefix(str(record['source_domain']), str(record['dataset_id']))}",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
