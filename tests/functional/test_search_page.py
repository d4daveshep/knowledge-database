from playwright.sync_api import Page, expect


def test_search_page(my_base_url: str, page: Page):
    page.goto(my_base_url + "/search")

    # title is Search
    expect(page).to_have_title("Search")

    # heading is Search
    heading = page.get_by_role("heading", name="Search")
    expect(heading).to_have_text("Search")

    assert False
