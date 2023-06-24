import re

from playwright.sync_api import Page, expect


def add_new_connection(page: Page, subject_name: str, conn_name: str, target_name: str):
    expect(page).to_have_title("Add Connection")

    subject_field = page.get_by_label("Subject")
    expect(subject_field).to_be_empty()
    expect(subject_field).to_be_editable()
    subject_field.fill(subject_name)

    target_field = page.get_by_label("Target")
    expect(target_field).to_be_empty()
    expect(target_field).to_be_editable()
    target_field.fill(target_name)

    conn_name_field = page.get_by_label("Connection")
    expect(conn_name_field).to_be_empty()
    expect(conn_name_field).to_be_editable()
    conn_name_field.fill(conn_name)

    # click the submit button
    submit_button = page.get_by_role("button", name="Add Connection")
    submit_button.click()


def check_added_connection_links(page: Page, subject_name: str, conn_name: str, target_name: str) -> tuple:
    new_subject_link = page.get_by_role("link", name=subject_name)
    expect(new_subject_link).to_have_text(subject_name)
    expect(new_subject_link).to_have_attribute("href", re.compile("/connections-to-node/[0-9]+"))

    new_target_link = page.get_by_role("link", name=target_name)
    expect(new_target_link).to_have_text(target_name)
    expect(new_target_link).to_have_attribute("href", re.compile("/connections-to-node/[0-9]+"))

    new_name_link = page.get_by_role("link", name=conn_name)
    expect(new_name_link).to_have_text(conn_name)
    expect(new_name_link).to_have_attribute("href", f"/connections/?name_like={conn_name.replace(' ', '+')}")

    return new_subject_link, new_target_link, new_name_link


def test_add_connection(page: Page, purge_database):
    # browse to the home page
    page.goto("http://localhost:8000/home")
    expect(page).to_have_title("Home")

    # find the link to add a connection
    add_connection_link = page.get_by_role("link", name="Add Connection")
    expect(add_connection_link).to_have_text("Add Connection")
    expect(add_connection_link).to_have_attribute("href", "/add-connection")

    # click the link to a add connection
    add_connection_link.click()

    # enter the connection that "Andrew is a Chief Engineer"
    add_new_connection(page, "Andrew", "is a", "Chief Engineer")

    # arrive at page confirming connection added
    expect(page).to_have_title("Add Connection")

    # page displays the new connection as hyperlinks
    new_subject_link, new_target_link, new_name_link = check_added_connection_links(page, "Andrew", "is a",
                                                                                    "Chief Engineer")

    # click the subject Andrew
    new_subject_link.click()

    # takes us to the connections-to-node-results page
    expect(page).to_have_title("Connections to Node Results")

    # page displays the existing connections that Andrew has
    new_subject_link, new_target_link, new_name_link = check_added_connection_links(page, "Andrew", "is a",
                                                                                    "Chief Engineer")

    # click the connection name link
    new_name_link.click()

    # takes us to the connections results page
    expect(page).to_have_title("Connection Results")

    # page contains heading
    heading = page.get_by_role("heading", name="Connections like 'is a'")
    expect(heading).to_contain_text("is a")

    # page contains number found
    count = page.get_by_text(text=re.compile("Found [0-9]+"))
    expect(count).to_contain_text(expected=re.compile("[0-9]+"))

    # confirm again the new connection is there
    new_subject_link, new_target_link, new_name_link = check_added_connection_links(page, "Andrew", "is a",
                                                                                    "Chief Engineer")

    # enter another connection that "Andrew knows Java"
    page.goto("http://localhost:8000/add-connection")
    add_new_connection(page, "Andrew", "knows", "Java")

    # page displays the new connection as hyperlinks
    new_subject_link, new_target_link, new_name_link = check_added_connection_links(page, "Andrew", "knows", "Java")

    # TODO add tests for second connection
