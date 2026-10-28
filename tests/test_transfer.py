"""Moving a hunt to another device with a .json file: export in the parents' menu, import on a fresh device."""
import base64
import json

import pytest
from playwright.sync_api import expect

from test_reveal import PATTERN
from test_smoke import browser, open_parents  # noqa: F401  (the browser fixture is shared)

HUNT = {
    "title": "Overzet-test",
    "story": "Zoek de plek.",
    "culpritIndex": 0,
    "suspects": ["Papa", "Mama"],
    "finalHide": "In de schuur",
    "steps": [{"type": "match", "clue": "", "hint": "", "evidence": "Voetstappen!"}],
}


@pytest.fixture
def new_page(browser, base_url):  # noqa: F811
    contexts, errors = [], []

    def make(cfg=None):
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, locale="nl-NL", accept_downloads=True)
        contexts.append(ctx)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(base_url)
        if cfg:
            pg.evaluate("cfg => localStorage.setItem('speurtocht.config.v1', JSON.stringify(cfg))", cfg)
            pg.reload()
        return pg

    yield make
    for ctx in contexts:
        ctx.close()
    assert not errors, f"JavaScript errors on the page: {errors}"


def test_export_and_import_json_file_with_photos(new_page, tmp_path):
    page = new_page(HUNT)
    open_parents(page)
    page.locator(".step-toggle").first.click()
    png = base64.b64decode(page.evaluate(PATTERN).split(",")[1])
    page.locator('input[data-photo="0"]').set_input_files({"name": "plek.png", "mimeType": "image/png", "buffer": png})
    expect(page.locator(".step-edit img.thumb")).to_be_visible()

    page.get_by_role("tab", name="Instellingen").click()
    with page.expect_download() as dl:
        page.get_by_role("button", name="Bewaar als bestand").click()
    assert dl.value.suggested_filename == "Overzet-test.json"
    path = tmp_path / "tocht.json"
    dl.value.save_as(path)
    data = json.loads(path.read_text())
    step = data["cfg"]["steps"][0]
    assert data["cfg"]["title"] == "Overzet-test"
    assert set(data["images"]) == {step["photo"], step["sketch"]}
    assert all(v.startswith("data:image/") for v in data["images"].values())

    other = new_page()  # another device: the example hunt, no photos
    open_parents(other)
    other.get_by_role("tab", name="Instellingen").click()
    other.locator("#importFile").set_input_files(str(path))
    expect(other.get_by_text("Instellingen overgenomen met 2 foto's.")).to_be_visible()
    assert other.evaluate("JSON.parse(localStorage.getItem('speurtocht.config.v1')).title") == "Overzet-test"

    other.reload()  # the photos are stored on the new device
    open_parents(other)
    other.locator(".step-toggle").first.click()
    expect(other.locator(".step-edit img.thumb")).to_be_visible()


def test_import_rejects_a_wrong_file(new_page, tmp_path):
    page = new_page()
    open_parents(page)
    page.get_by_role("tab", name="Instellingen").click()
    bad = tmp_path / "nee.json"
    bad.write_text('{"hallo": 1}')
    page.locator("#importFile").set_input_files(str(bad))
    expect(page.get_by_text("Dat bestand klopt niet.", exact=False)).to_be_visible()
