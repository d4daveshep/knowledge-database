def test_db_setup(db_cursor):
    result = db_cursor.execute("SELECT name FROM sqlite_master")
    assert result.fetchall() == [("nodes",), ("connections",)]

    pass


def test_db_populated(db_populate):
    result = db_populate.execute("SELECT name FROM nodes")
    names = result.fetchall()
    assert len(names) == 14

    # assert names[0] == ("Andrew",)
