from playwright.sync_api import Page, expect


def test_add_connection(page:Page):
    # browse to the home page
    page.goto("http://127.0.0.1:8000/home")
    expect(page).to_have_title("Home")

    # find the link to add knowledge
    add_connection_link = page.get_by_role("link", name="Add Connection")
    expect(add_connection_link).to_have_text("Add Connection")
    expect(add_connection_link).to_have_attribute("href", "/add-connection")

    # click the link to add connection
    add_connection_link.click()
    expect(page).to_have_title("Add Connection")


    # enter the connection that "Andrew is a Chief Engineer"
    subject_field = page.get_by_label("like")
    assert False

    # page displays the new connection as hyperlinks

    # click the subject Andrew

    # page displays the existing connections that Andrew has

    # confirm the new connection is listed

    # enter another connection that "Andrew knows Java"





    # assert False