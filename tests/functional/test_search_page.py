from playwright.sync_api import Page, expect


def test_search_page(my_base_url: str, page: Page):
    page.goto(my_base_url + "/search")

    # title is Search
    expect(page).to_have_title("Search")

    # heading is Search
    heading = page.get_by_role("heading", name="Search")
    expect(heading).to_have_text("Search")

    # there is a text field labeled Search

    # and a submit button

    # when I enter a node name and hit submit I go to the Conections to a Node page

    # and at least one node I searched for is there

    assert False
