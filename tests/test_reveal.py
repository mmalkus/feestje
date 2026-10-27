"""The surprise photo of a "Zoek deze plek" step: made by the AI in the parents' menu, shown when the kids find the spot."""
import base64
import json
import re

import pytest
from playwright.sync_api import expect

from test_smoke import browser, open_parents  # noqa: F401  (the browser fixture is shared)

HUNT = {
    "title": "Verrassingstest",
    "story": "Zoek de plek.",
    "culpritIndex": 0,
    "suspects": ["Papa", "Mama"],
    "finalHide": "In de schuur",
    "steps": [{"type": "match", "clue": "", "hint": "", "evidence": "Voetstappen!"}],
}
AI = {"provider": "openai", "base": "https://api.openai.com/v1", "style": "edits", "model": "gpt-image-1",
      "keys": {"openai": "sk-test"}}
CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"}

# A busy pattern, so the spot check in the parents' menu has corners to find.
PATTERN = """() => { const c = document.createElement("canvas"); c.width = 640; c.height = 480; const x = c.getContext("2d");
  let s = 7; const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
  x.fillStyle = "#ddd"; x.fillRect(0, 0, 640, 480);
  for (let i = 0; i < 150; i++){ x.fillStyle = `hsl(${r()*360},60%,${20 + r()*60}%)`; x.fillRect(r()*620, r()*460, 10 + r()*60, 10 + r()*60); }
  return c.toDataURL("image/png"); }"""


@pytest.fixture
def page(browser, base_url):  # noqa: F811
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, locale="nl-NL")
    errors, prompts = [], []

    def edits(route):
        if route.request.method == "OPTIONS":
            return route.fulfill(status=204, headers=CORS)
        prompts.append(route.request.post_data_buffer)
        red = page.evaluate("""() => { const c = document.createElement("canvas"); c.width = c.height = 64;
          const x = c.getContext("2d"); x.fillStyle = "red"; x.fillRect(0, 0, 64, 64); return c.toDataURL("image/png").split(",")[1]; }""")
        route.fulfill(status=200, headers={**CORS, "Content-Type": "application/json"}, body=json.dumps({"data": [{"b64_json": red}]}))

    ctx.route("**/images/edits", edits)
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base_url)
    page.evaluate("([cfg, ai]) => { localStorage.setItem('speurtocht.config.v1', JSON.stringify(cfg)); localStorage.setItem('speurtocht.ai.v1', JSON.stringify(ai)); }", [HUNT, AI])
    page.reload()
    page.prompts = prompts
    yield page
    ctx.close()
    assert not errors, f"JavaScript errors on the page: {errors}"


def test_surprise_photo_is_made_in_setup_and_shown_when_the_spot_is_found(page):
    open_parents(page)
    page.locator(".step-toggle").first.click()
    png = base64.b64decode(page.evaluate(PATTERN).split(",")[1])
    page.locator('input[data-photo="0"]').set_input_files({"name": "plek.png", "mimeType": "image/png", "buffer": png})
    expect(page.get_by_role("button", name="Maak verrassingsfoto")).to_be_enabled()

    page.fill("#revealWhat-0", "modderige voetstappen om de hoek")
    page.get_by_role("button", name="Maak verrassingsfoto").click()
    expect(page.get_by_alt_text("Verrassingsfoto")).to_be_visible()
    assert b"modderige voetstappen om de hoek" in page.prompts[0]
    page.get_by_role("button", name="Opslaan").click()
    expect(page.get_by_text("Opgeslagen.")).to_be_visible()

    page.reload()  # the surprise is kept on the device (IndexedDB)
    page.fill("#team", "De Testers")
    page.get_by_role("button", name="Start het onderzoek").click()
    page.get_by_role("button", name="Zoeken maar!").click()
    expect(page.get_by_alt_text("Kijk eens wat er op deze plek gebeurd is!")).to_have_count(0)  # not before it's found
    page.get_by_role("button", name="Ouders: plek goedkeuren").click()
    a, b = map(int, re.search(r"(\d+) × (\d+)", page.locator(".overlay").inner_text()).groups())
    page.fill("#approve", str(a * b))
    page.get_by_role("button", name="Goedkeuren", exact=True).click()
    expect(page.get_by_text("PLEK GEVONDEN!")).to_be_visible()
    expect(page.get_by_alt_text("Kijk eens wat er op deze plek gebeurd is!")).to_be_visible()
    expect(page.get_by_text("Voetstappen!")).to_be_visible()


def test_new_photo_drops_the_old_surprise(page):
    open_parents(page)
    page.locator(".step-toggle").first.click()
    png = base64.b64decode(page.evaluate(PATTERN).split(",")[1])
    photo = page.locator('input[data-photo="0"]')
    photo.set_input_files({"name": "plek.png", "mimeType": "image/png", "buffer": png})
    page.fill("#revealWhat-0", "een spinnenweb")
    page.get_by_role("button", name="Maak verrassingsfoto").click()
    expect(page.get_by_alt_text("Verrassingsfoto")).to_be_visible()
    photo.set_input_files({"name": "plek2.png", "mimeType": "image/png", "buffer": png})
    expect(page.get_by_alt_text("Verrassingsfoto")).to_have_count(0)
    expect(page.locator("#revealWhat-0")).to_have_value("een spinnenweb")  # the wish stays, ready to make again
