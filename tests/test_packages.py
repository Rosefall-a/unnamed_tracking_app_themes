"""Exercise the actual archive builder and reject invalid source packages."""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.build_themes import ROOT, build, package_theme


class ThemePackageTests(unittest.TestCase):
    """Verify reproducible sharing and bounded, executable-free package inputs."""

    def test_the_repository_builds_identical_inert_archives(self):
        """Both source collections produce installable archives without build-time entropy."""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            first = build(ROOT, output)
            payloads = {row["package"]: (output / row["package"]).read_bytes() for row in first}
            self.assertEqual(first, build(ROOT, output))
            self.assertEqual(len(first), 2)
            for name, original in payloads.items():
                self.assertEqual(original, (output / name).read_bytes())
                with zipfile.ZipFile(output / name) as archive:
                    manifest = json.loads(archive.read("manifest.json"))
                    self.assertIn(manifest["stylesheet"], archive.namelist())
                    self.assertFalse(
                        any(item.endswith((".js", ".py")) for item in archive.namelist())
                    )

    def test_missing_stylesheet_and_executable_assets_are_rejected(self):
        """An installer must never receive a manifest with absent CSS or a worker."""
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            manifest = json.loads((ROOT / "official/forest/manifest.json").read_text())
            (source / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "missing"):
                package_theme(source, Path(temporary) / "output")
            (source / "theme.css").write_text("html { color: purple; }")
            (source / "worker.py").write_text("raise RuntimeError('must not ship')")
            with self.assertRaisesRegex(ValueError, "Unsupported"):
                package_theme(source, Path(temporary) / "output")

    def test_parent_paths_and_reserved_identifiers_are_rejected(self):
        """Manifest paths cannot pull unrelated files into a shared archive."""
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            original = json.loads((ROOT / "official/forest/manifest.json").read_text())
            for field, value in (
                ("stylesheet", "../theme.css"),
                ("stylesheet", "/theme.css"),
                ("id", "native"),
            ):
                (source / "manifest.json").write_text(json.dumps({**original, field: value}))
                with self.assertRaises(ValueError):
                    package_theme(source, source / "output")


if __name__ == "__main__":
    unittest.main()
