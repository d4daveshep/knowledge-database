from playwright.sync_api import Page, expect


def test_search_page(loaded_test_data, my_base_url: str, page: Page):
    page.goto(my_base_url + "/search")

    # title is Search
    expect(page).to_have_title("Search")

    # heading is Search
    heading = page.get_by_role("heading", name="Search")
    expect(heading).to_have_text("Search")

    # there is a text field labeled Search
    search_field = page.get_by_label("Search")
    expect(search_field).to_be_empty()
    expect(search_field).to_be_editable()

    # and a submit button
    submit_button = page.get_by_role("button", name="Search")

    # when I enter a node name and hit submit I go to the Connections to a Node page
    search_field.fill("Andrew")
    submit_button.click()

    expect(page).to_have_title("Connections to a Node")

    # and at least one node I searched for is there

    # assert False
