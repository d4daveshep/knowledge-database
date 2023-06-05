from playwright.sync_api import Page


def test_add_connection(page:Page):
    # browse to the home page
    page.goto("http://127.0.0.1:8000/home")

    # click the link to add knowledge
    add_connection_link = page.get_by_role("link", name="Add Connection")
    assert add_connection_link.text_content() == "Add Connection"
    add_connection_link.click()


    # enter the connection that "Andrew is a Chief Engineer"

    # page displays the new connection as hyperlinks

    # click the subject Andrew

    # page displays the existing connections that Andrew has

    # confirm the new connection is listed

    # enter another connection that "Andrew knows Java"





    assert False