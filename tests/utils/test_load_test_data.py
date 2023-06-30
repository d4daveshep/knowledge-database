"""
Test the loading of test data into the current database
"""
from sqlalchemy.orm import Session

from web_apps import crud, models


def test_load_test_data(db_session:Session):

    # purge the database
    crud.delete_nodes(db_session)

    # load test data
    crud.load_test_data(db_session)

    # check row counts
    assert crud.get_table_size(db_session,models.Node) == 15
    assert crud.get_table_size(db_session,models.Connection) == 17

