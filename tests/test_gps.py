"""The "Kompastocht (GPS)" step: walking to a point with the compass, and setting the point in the parents' menu."""
import json
import re

import pytest
from playwright.sync_api import expect

from test_smoke import browser, open_parents  # noqa: F401  (the browser fixture is shared)

TARGET = {"latitude": 52.090737, "longitude": 5.121420}
FAR = {"latitude": 52.092537, "longitude": 5.121420}  # about 200 m north of the target

TRAIL = {
    "title": "Kompastest",
    "story": "Volg de pijl.",
    "culpritIndex": 0,
    "suspects": ["Papa", "Mama"],
    "finalHide": "In de schuur",
    "steps": [
        {"type": "gps", "pos": "52.090737, 5.121420", "radius": 20, "clue": "Loop naar de boom.", "hint": "", "evidence": "Een veer!"},
        {"type": "gps", "pos": "52.091737, 5.121420", "radius": 20, "clue": "", "hint": "", "evidence": ""},
    ],
}


@pytest.fixture
def ctx(browser, base_url):  # noqa: F811
    c = browser.new_context(viewport={"width": 390, "height": 844}, locale="nl-NL",
                            geolocation=FAR, permissions=["geolocation"])
    errors = []
    c.on("weberror", lambda e: errors.append(str(e.error)))
    yield c
    c.close()
    assert not errors, f"JavaScript errors on the page: {errors}"


def start_trail(ctx, base_url):
    page = ctx.new_page()
    page.goto(base_url)
    page.evaluate("cfg => localStorage.setItem('speurtocht.config.v1', JSON.stringify(cfg))", TRAIL)
    page.reload()
    page.fill("#team", "De Testers")
    page.get_by_role("button", name="Start het onderzoek").click()
    return page


def test_walking_to_the_point_solves_the_step(ctx, base_url):
    page = start_trail(ctx, base_url)
    expect(page.get_by_text("Loop naar de boom.")).to_be_visible()
    page.get_by_role("button", name="Op pad!").click()
    expect(page.locator("#compass")).to_be_visible()
    expect(page.locator("#gpsDist")).to_have_text(re.compile(r"Nog 20\d meter"))

    ctx.set_geolocation({"latitude": 52.091537, "longitude": 5.121420})  # 89 m to go
    expect(page.locator("#gpsDist")).to_have_text(re.compile(r"Warmer!.*Nog \d\d meter"))
    # no compass in a desktop browser: the arrow shows the map direction, here straight south
    expect(page.locator("#needle")).to_have_attribute("style", re.compile(r"rotate\(-?180deg\)"))

    ctx.set_geolocation(TARGET)
    expect(page.get_by_text("PLEK GEVONDEN!")).to_be_visible()
    expect(page.get_by_text("Een veer!")).to_be_visible()
    page.get_by_role("button", name="Volgende opdracht").click()
    expect(page.get_by_text("Stap 2/2")).to_be_visible()
    expect(page.get_by_role("button", name="Op pad!")).to_be_visible()


def test_parent_can_approve_the_point(ctx, base_url):
    page = start_trail(ctx, base_url)
    page.get_by_role("button", name="Op pad!").click()
    page.get_by_role("button", name="Ouders: we zijn er").click()
    a, b = map(int, re.search(r"(\d+) × (\d+)", page.locator(".overlay").inner_text()).groups())
    page.fill("#approve", str(a * b))
    page.get_by_role("button", name="Goedkeuren").click()
    expect(page.get_by_text("PLEK GEVONDEN!")).to_be_visible()


def test_point_from_a_maps_link_in_the_parents_menu(ctx, base_url):
    page = ctx.new_page()
    page.goto(base_url)
    open_parents(page)
    page.locator(".step-toggle").first.click()
    page.select_option("#type-0", "gps")
    expect(page.locator("[data-map='0']")).to_be_visible()
    page.get_by_role("button", name="Opslaan").click()
    expect(page.locator("#setupMsg")).to_have_text("Stap 1 mist nog een plek op de kaart.")

    page.fill("#pos-0", "https://www.google.com/maps/@52.0907374,5.1214201,17z")
    expect(page.locator("#gpsInfo-0")).to_have_text("Eerste punt van de kompastocht")
    page.select_option("#radius-0", "30")
    page.get_by_role("button", name="Opslaan").click()
    expect(page.locator("#setupMsg")).to_have_text("Opgeslagen.")
    step = json.loads(page.evaluate("localStorage.getItem('speurtocht.config.v1')"))["steps"][0]
    assert step["type"] == "gps" and step["radius"] == "30" and "52.0907374,5.1214201" in step["pos"]
