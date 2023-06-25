import pytest
from playwright.sync_api import Page
from playwright.sync_api import expect

@pytest.fixture
def my_base_url()->str:
    return "http://localhost:8000"

# @pytest.fixture
# def purge_database(my_base_url:str, page: Page):
#     # browse to the purge database page
#     page.goto(my_base_url + "/purge-database")
#     expect(page).to_have_title("Purge Database")
#
#     # click the confirm button
#     purge_button = page.get_by_role("button", name="Purge Database")
#     purge_button.click()
#
#     # expect to be at database stats page
#     expect(page).to_have_title("Database Stats")
#     node_count = page.get_by_text("Nodes")
#     expect(node_count).to_contain_text("0")
#     connection_count = page.get_by_text("Connections")
#     expect(connection_count).to_contain_text("0")
