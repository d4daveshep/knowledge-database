import pytest
from playwright.sync_api import Page
from playwright.sync_api import expect

@pytest.fixture
def my_base_url()->str:
    return "http://localhost:8000"

@pytest.fixture
def purge_database(my_base_url:str, page: Page):
    # browse to the purge database page
    page.goto(my_base_url + "/purge-database")
    expect(page).to_have_title("Purge Database")

    # click the confirm button
    purge_button = page.get_by_role("button", name="Purge Database")
    purge_button.click()

@pytest.fixture
def loaded_test_data(purge_database, my_base_url, page:Page):
    # browse to the (hidden) load test data page
    page.goto(my_base_url+"/load-test-data")
    expect(page).to_have_title("Load Test Data")

    # click the button
    load_button = page.get_by_role("button", name="Load Test Data")
    load_button.click()
