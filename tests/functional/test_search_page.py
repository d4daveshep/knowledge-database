import re

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
    # searching_for = "Andrew"
    searching_for = "e"
    search_field.fill(value=searching_for)
    submit_button.click()

    expect(page).to_have_title("Search Results")

    # and at least one node I searched for is there
    expect(page.get_by_text("Found 7 Nodes")).to_be_visible()

    # and at least one connection I searched for is there
    expect(page.get_by_text("Found 3 Connections")).to_be_visible()

    links = page.get_by_role("listitem")
    expect(links).to_have_count(10)

    # assert False

"""
"""