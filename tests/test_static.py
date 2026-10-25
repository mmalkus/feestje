"""Checks that need no browser: versions in sync, files referenced by the PWA exist, scripts parse."""
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pytest


def read(root, name):
    return (root / name).read_text(encoding="utf-8")


def test_version_matches_service_worker_cache(root):
    # Phones only pick up a new release when the cache name in sw.js changes, so both must move together.
    version = re.search(r"const VERSION\s*=\s*(\d+)\s*;", read(root, "index.html"))
    cache = re.search(r'const C\s*=\s*"speurtocht-v(\d+)"', read(root, "sw.js"))
    assert version and cache, "VERSION in index.html or cache name in sw.js not found"
    assert version.group(1) == cache.group(1), (
        f"index.html VERSION={version.group(1)} but sw.js caches speurtocht-v{cache.group(1)}; bump both"
    )


def test_service_worker_precache_files_exist(root):
    files = json.loads(re.search(r"const FILES\s*=\s*(\[.*?\])\s*;", read(root, "sw.js")).group(1))
    for f in files:
        if f in ("./", "/"):
            continue
        assert (root / f).is_file(), f"sw.js precaches {f}, which is not in the repo"


def test_manifest_is_valid_and_icons_exist(root):
    m = json.loads(read(root, "manifest.webmanifest"))
    for key in ("name", "short_name", "start_url", "display", "icons"):
        assert key in m, f"manifest is missing '{key}'"
    for icon in m["icons"]:
        assert (root / icon["src"]).is_file(), f"manifest icon {icon['src']} is missing"
    assert 'rel="manifest"' in read(root, "index.html")


def test_icon_svg_is_well_formed(root):
    assert ET.fromstring(read(root, "icon.svg")).tag.endswith("svg")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_inline_scripts_parse(root, tmp_path):
    scripts = re.findall(r"<script>(.*?)</script>", read(root, "index.html"), flags=re.S)
    assert scripts, "no inline <script> found in index.html"
    for i, src in enumerate(scripts + [read(root, "sw.js")]):
        f = tmp_path / f"script{i}.js"
        f.write_text(src, encoding="utf-8")
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, f"script {i} has a syntax error:\n{r.stderr}"
