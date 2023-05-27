def test_db_tables_setup(db_cursor):
    result = db_cursor.execute("SELECT name FROM sqlite_master")
    assert result.fetchall() == [("nodes",), ("connections",)]

    pass


def test_db_populated(db_populated):
    result = db_populated.execute("SELECT name FROM nodes")
    node_names = result.fetchall()
    assert len(node_names) == 15

    result = db_populated.execute("SELECT name, subject_id, target_id FROM connections")
    connections = result.fetchall()
    assert len(connections) == 17

    # assert names[0] == ("Andrew",)
