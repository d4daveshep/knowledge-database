from playwright.sync_api import Page, expect


def test_search_page(page: Page):
    page.goto("http://127.0.0.1:8000/search")
    expect(page).to_have_title("Search")
