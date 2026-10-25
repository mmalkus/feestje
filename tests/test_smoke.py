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


def gate_answer(page, offset=0):
    question = page.get_by_text(re.compile(r"hoeveel is \d+ × \d+")).inner_text()
    a, b = map(int, re.search(r"(\d+) × (\d+)", question).groups())
    page.fill("#gate", str(a * b + offset))
    page.get_by_role("button", name="Open").click()


def open_parents(page):
    page.get_by_role("button", name="Ouders").click()
    gate_answer(page)
    expect(page.get_by_text(re.compile(r"Versie \d+"))).to_be_visible()


def step_titles(page):
    return page.locator(".step-toggle b").all_inner_texts()


def test_parent_gate(page):
    page.get_by_role("button", name="Ouders").click()
    gate_answer(page, offset=1)
    expect(page.locator("#gate")).to_be_visible()  # wrong answer: still locked

    gate_answer(page)
    expect(page.get_by_text(re.compile(r"Versie \d+"))).to_be_visible()


def test_parents_menu_has_separate_tabs(page):
    open_parents(page)
    expect(page.get_by_role("tab", name="Opdrachten")).to_have_attribute("aria-selected", "true")
    expect(page.locator(".step-edit")).to_have_count(8)
    expect(page.locator("#ai-key")).to_be_hidden()

    page.get_by_role("tab", name="Instellingen").click()
    expect(page.locator("#ai-key")).to_be_visible()
    expect(page.locator(".step-edit").first).to_be_hidden()


def test_steps_fold_open_and_closed(page):
    open_parents(page)
    expect(page.locator("#clue-1")).to_be_hidden()  # folded by default
    page.locator(".step-toggle").nth(1).click()
    expect(page.locator("#clue-1")).to_be_visible()
    page.fill("#clue-1", "Nieuw raadsel")
    page.locator(".step-toggle").nth(1).click()
    expect(page.locator("#clue-1")).to_be_hidden()
    page.get_by_role("button", name="Alles open").click()
    expect(page.locator("#clue-1")).to_have_value("Nieuw raadsel")  # typed text survives folding
    expect(page.locator("#clue-7")).to_be_visible()


def test_drag_changes_step_order(page):
    open_parents(page)
    first = step_titles(page)
    page.locator("#steps").evaluate("e => e.scrollIntoView()")  # away from the edges, where dragging scrolls the page
    handle = page.locator("[data-drag='0']").bounding_box()
    target = page.locator(".step-edit").nth(2).bounding_box()
    page.mouse.move(handle["x"] + handle["width"] / 2, handle["y"] + handle["height"] / 2)
    page.mouse.down()
    page.mouse.move(handle["x"] + 10, target["y"] + target["height"] * 0.75, steps=12)
    page.wait_for_timeout(100)  # the drag follows the pointer on animation frames
    page.mouse.up()
    titles = step_titles(page)
    assert [t.split("·", 1)[1] for t in titles[:3]] == [first[1].split("·", 1)[1], first[2].split("·", 1)[1], first[0].split("·", 1)[1]]
    assert titles[0].startswith("▸ Stap 1")

    page.get_by_role("button", name="Opslaan").click()
    expect(page.locator("#setupMsg")).to_have_text("Opgeslagen.")
    saved = page.evaluate("JSON.parse(localStorage.getItem('speurtocht.config.v1')).steps.map(s => s.type)")
    assert saved[:3] == ["code", "code", "camera"]


def test_arrow_keys_move_a_step(page):
    open_parents(page)
    page.locator("[data-drag='0']").focus()
    page.keyboard.press("ArrowDown")
    expect(page.locator("[data-drag='1']")).to_be_focused()
    assert "Raadsel" in step_titles(page)[0] and "Foto-opdracht" in step_titles(page)[1]


def test_works_offline_after_first_visit(page):
    page.evaluate("navigator.serviceWorker.ready")
    page.reload()  # let the service worker take control and cache the files
    page.wait_for_function("navigator.serviceWorker.controller !== null")
    page.context.set_offline(True)
    page.reload()
    expect(page.locator("h1")).to_have_text("De Verdwenen Verjaardagstaart")
