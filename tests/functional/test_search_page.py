from playwright.sync_api import Page, expect


def test_search_page(my_base_url: str, page: Page):
    page.goto(my_base_url + "/search")
    expect(page).to_have_title("Search")
