from playwright.sync_api import Page, expect


def test_add_connection(page: Page):
    # browse to the home page
    page.goto("http://127.0.0.1:8000/home")
    expect(page).to_have_title("Home")

    # find the link to add a connection
    add_connection_link = page.get_by_role("link", name="Add Connection")
    expect(add_connection_link).to_have_text("Add Connection")
    expect(add_connection_link).to_have_attribute("href", "/add-connection")

    # click the link to a add connection
    add_connection_link.click()
    expect(page).to_have_title("Add Connection")

    # enter the connection that "Andrew is a Chief Engineer"
    # enter Andrew as the subject
    subject_field = page.get_by_label("Subject")
    expect(subject_field).to_be_empty()
    expect(subject_field).to_be_editable()
    subject_field.fill("Andrew")

    # enter Chief Engineer as the target
    target_field = page.get_by_label("Target")
    expect(target_field).to_be_empty()
    expect(target_field).to_be_editable()
    target_field.fill("Chief Engineer")

    # enter "is a" as the connection name
    conn_name_field = page.get_by_label("Connection")
    expect(conn_name_field).to_be_empty()
    expect(conn_name_field).to_be_editable()
    conn_name_field.fill("is a")

    # click the submit button
    submit_button = page.get_by_role("button", name="Add Connection")
    submit_button.click()

    # arrive at page confirming connection added
    expect(page).to_have_title("Connections")

    # page displays the new connection as hyperlinks
    new_subject_link = page.get_by_role("link", name="Andrew")
    expect(new_subject_link).to_have_text("Andrew")
    # expect(add_connection_link).to_have_attribute("href", "/add-connection")

    assert False


    # click the subject Andrew

    # page displays the existing connections that Andrew has

    # confirm the new connection is listed

    # enter another connection that "Andrew knows Java"

    # assert False
