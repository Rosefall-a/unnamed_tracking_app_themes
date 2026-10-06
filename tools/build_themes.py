"""Build deterministic, inert CSS theme packages from reviewed source directories."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {
    ".css",
    ".md",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".svg",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}
FIELDS = {
    "format_version",
    "id",
    "name",
    "version",
    "publisher",
    "description",
    "kind",
    "stylesheet",
    "supports",
}


def manifest_at(source: Path) -> dict[str, Any]:
    """Validate the public manifest before reading or including its stylesheet."""
    value = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("Use exactly the format 1 manifest fields")
    if isinstance(value["format_version"], bool) or value["format_version"] != 1:
        raise ValueError("Use exactly the format 1 manifest fields")
    identifier = value["id"]
    if (
        not isinstance(identifier, str)
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", identifier)
        or identifier in {"native", "server"}
    ):
        raise ValueError("Invalid or reserved theme identifier")
    if not isinstance(value["version"], str) or not re.fullmatch(
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value["version"]
    ):
        raise ValueError("Use a three-part numeric version")
    for field, maximum in (("name", 120), ("publisher", 120), ("description", 1000)):
        if (
            not isinstance(value[field], str)
            or not value[field].strip()
            or len(value[field]) > maximum
        ):
            raise ValueError(f"Invalid {field}")
    if value["kind"] not in {"official", "example"} or value["supports"] not in [
        ["light"],
        ["dark"],
        ["light", "dark"],
        ["dark", "light"],
    ]:
        raise ValueError("Choose a collection and supported light/dark modes")
    stylesheet = value["stylesheet"]
    if not isinstance(stylesheet, str) or "\\" in stylesheet or ":" in stylesheet:
        raise ValueError("Use a relative CSS path")
    path = PurePosixPath(stylesheet)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".css":
        raise ValueError("Use a relative CSS path")
    return value


def package_theme(source: Path, output: Path) -> dict[str, Any]:
    """Package bounded source assets without timestamps or platform-specific metadata."""
    manifest = manifest_at(source)
    files = {"manifest.json": (json.dumps(manifest, indent=2) + "\n").encode()}
    for file in sorted(source.rglob("*")):
        if file.is_symlink():
            raise ValueError("Theme sources cannot contain symlinks")
        if not file.is_file() or file.name == "manifest.json":
            continue
        if file.suffix.lower() not in EXTENSIONS:
            raise ValueError(f"Unsupported theme asset: {file.name}")
        data = file.read_bytes()
        if file.suffix == ".css":
            data.decode("utf-8")
            if len(data) > 1024 * 1024:
                raise ValueError("CSS exceeds 1 MiB")
        files[file.relative_to(source).as_posix()] = data
    if manifest["stylesheet"] not in files:
        raise ValueError("Declared stylesheet is missing")
    if len(files) > 128 or sum(map(len, files.values())) > 20 * 1024 * 1024:
        raise ValueError("Too many or oversized theme assets")
    output.mkdir(parents=True, exist_ok=True)
    destination = output / f"{manifest['id']}-{manifest['version']}.utt"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    if destination.stat().st_size > 10 * 1024 * 1024:
        destination.unlink()
        raise ValueError("Theme upload exceeds 10 MiB")
    return {
        **manifest,
        "package": destination.name,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }


def build(root: Path, output: Path) -> list[dict[str, Any]]:
    """Build the official and example collections, rejecting duplicate identities."""
    records = []
    identifiers = set()
    for collection in ("official", "examples"):
        for source in sorted((root / collection).glob("*/manifest.json")):
            record = package_theme(source.parent, output)
            if record["id"] in identifiers:
                raise ValueError("Duplicate theme identifier")
            identifiers.add(record["id"])
            records.append(record)
    if not records:
        raise ValueError("No theme sources found")
    (output / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return records


def main() -> None:
    """Expose a standard-library-only build command for branch artifact validation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "unsigned-dist")
    arguments = parser.parse_args()
    print(f"Built {len(build(ROOT, arguments.output))} CSS themes")


if __name__ == "__main__":
    main()
