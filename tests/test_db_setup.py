from web_apps import crud, models


def test_db_tables_setup(db_cursor):
    result = db_cursor.execute("SELECT name FROM sqlite_master")
    assert result.fetchall() == [("nodes",), ("connections",)]

    pass


def test_fixture(db_session):
    nodes = crud.get_nodes(db_session)
    assert len(nodes) == 15
    assert crud.get_table_size(db_session, models.Node) == 15

    connections = crud.get_connections(db_session)
    assert len(connections) == 17
    assert crud.get_table_size(db_session, models.Connection) == 17

