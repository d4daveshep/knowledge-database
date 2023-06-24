import re

from playwright.sync_api import Page, expect


def test_database_stats(my_base_url: str, page: Page):
    page.goto(my_base_url + "/database-stats")

    # expect to be at database stats page
    expect(page).to_have_title("Database Stats")
    node_count = page.get_by_text("Nodes")
    expect(node_count).to_contain_text(re.compile("Nodes: [0-9]+"))
    connection_count = page.get_by_text("Connections")
    expect(connection_count).to_contain_text(re.compile("Connections: [0-9]+"))
