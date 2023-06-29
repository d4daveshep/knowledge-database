"""
Test that we can purge the database and load test data.
We'll then use this as a fixture in other functional tests
"""
from playwright.sync_api import expect, Page


def test_purge_database(my_base_url: str, page: Page):
    page.goto(my_base_url)
    page.get_by_role("link", name="Purge Database").click()
    expect(page).to_have_title("Purge Database")

    page.get_by_role("button", name="Purge Database").click()
    expect(page).to_have_title("Database Stats")

    node_count = page.get_by_text("Nodes")
    expect(node_count).to_have_text("Nodes: 0")
    connection_count = page.get_by_text("Connections")
    expect(connection_count).to_have_text("Connections: 0")
