import re

import pytest
from playwright.sync_api import expect, Page, Locator


@pytest.fixture
def home_page(page:Page)->Page:
    page.goto("http://127.0.0.1:8000/home")
    yield page



def test_title_contains_home(home_page:Page):
    expect(home_page).to_have_title("Home")

def test_nav_contains_home_link(home_page:Page):
    nav_home:Locator = home_page.get_by_role("link", name="Home")
    expect(nav_home).to_have_attribute("href", "/")

def test_nav_about_link(home_page:Page):
    nav_about:Locator = home_page.get_by_role("link", name="About")
    expect(nav_about).to_have_attribute("href", "/about")

    nav_about.click()
    about_page:Page = home_page
    expect(about_page).to_have_url(re.compile(".*about"))
    expect(about_page).to_have_title("About")




