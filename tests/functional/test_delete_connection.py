from playwright.sync_api import Page, expect


def test_delete_single_connection(loaded_test_data, my_base_url:str, page: Page):
    # search for some connections
    page.goto(my_base_url+"/connections/?name_like=e")
    # TODO get the number of connections so we can reduce by one

    # click the delete button for the 2nd row (Brian has title Practice Lead)
    delete_button_2 = page.get_by_role("button", name="Delete").nth(1) # zero based
    expect(delete_button_2).to_have_attribute(name="type",value="submit")
    expect(delete_button_2).to_have_attribute(name="formmethod",value="get")
    expect(delete_button_2).to_have_attribute(name="formaction",value="/delete-connection/2")

    # refresh the page and the connection should not be there
    delete_button_2.click()

    expect(page).to_have_title("Connection Results")

    # check the connections found is one less than previously

    # check the connection we delete isn't there

    assert False, "Wire up this function to some real database work"