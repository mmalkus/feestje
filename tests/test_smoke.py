"""Browser smoke tests (Playwright, Chromium, phone-sized viewport)."""
import re

import pytest
from playwright.sync_api import expect, sync_playwright


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(browser, base_url):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, locale="nl-NL")
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(base_url)
    yield pg
    ctx.close()
    assert not errors, f"JavaScript errors on the page: {errors}"


def test_start_screen(page):
    expect(page.locator("h1")).to_have_text("De Verdwenen Verjaardagstaart")
    expect(page.get_by_role("button", name="Start het onderzoek")).to_be_visible()
    expect(page.get_by_role("button", name="Ouders")).to_be_visible()


def test_begin_shows_first_assignment(page):
    page.fill("#team", "De Testers")
    page.get_by_role("button", name="Start het onderzoek").click()
    expect(page.get_by_role("button", name="Start het onderzoek")).to_have_count(0)
    expect(page.locator("#app")).not_to_be_empty()


def test_parent_gate(page):
    page.get_by_role("button", name="Ouders").click()
    question = page.get_by_text(re.compile(r"hoeveel is \d+ × \d+")).inner_text()
    a, b = map(int, re.search(r"(\d+) × (\d+)", question).groups())

    page.fill("#gate", str(a * b + 1))
    page.get_by_role("button", name="Open").click()
    expect(page.locator("#gate")).to_be_visible()  # wrong answer: still locked

    question = page.get_by_text(re.compile(r"hoeveel is \d+ × \d+")).inner_text()
    a, b = map(int, re.search(r"(\d+) × (\d+)", question).groups())
    page.fill("#gate", str(a * b))
    page.get_by_role("button", name="Open").click()
    expect(page.get_by_text(re.compile(r"Versie \d+"))).to_be_visible()


def test_works_offline_after_first_visit(page):
    page.evaluate("navigator.serviceWorker.ready")
    page.reload()  # let the service worker take control and cache the files
    page.wait_for_function("navigator.serviceWorker.controller !== null")
    page.context.set_offline(True)
    page.reload()
    expect(page.locator("h1")).to_have_text("De Verdwenen Verjaardagstaart")
