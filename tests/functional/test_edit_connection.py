import re

from playwright.sync_api import Page, expect


def test_edit_single_connection_name(loaded_test_data,my_base_url:str,page:Page):
    # search for some connections
    page.goto(my_base_url + "/connections/?name_like=has+title")
    orig_found_heading = page.get_by_role("heading", name=re.compile("Found [0-9]+ Connections"))
    expect(orig_found_heading).to_contain_text("3")

    # click an edit button in RH column
    button_2 = page.get_by_role("row", name="Brian has title Practice Lead Edit").get_by_role("button", name="Edit")
    button_2.click()

    # should go to the edit connection page
    expect(page).to_have_title("Edit Connection")

    # change the connection name

    # click button to change just this connection name

    # check I'm back on the connections to node page

    # and my connection name has changed

    assert False, "TODO do something more here"