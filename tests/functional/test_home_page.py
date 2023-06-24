import pytest
from playwright.sync_api import expect, Page, Locator


@pytest.fixture
def home_page(my_base_url: str, page: Page) -> Page:
    page.goto(my_base_url + "/home")
    yield page


def test_title_contains_home(home_page: Page):
    expect(home_page).to_have_title("Home")


def test_nav_contains_home_link(home_page: Page):
    nav_home: Locator = home_page.get_by_role("link", name="Home")
    expect(nav_home).to_have_attribute("href", "/home")


def test_root_is_home_page(my_base_url: str, page: Page):
    page.goto(my_base_url + "/")
    expect(page).to_have_title("Home")
