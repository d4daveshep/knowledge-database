from web_apps import crud, models
from web_apps.schemas import NodeCreate


def test_create_node(db_session):
    name = "Chris"
    node = crud.create_node(db_session, NodeCreate(name=name))
    assert node.name == name
    assert node.id


def test_get_node_by_id(db_session):
    node = crud.get_node(db_session, 2)
    assert node.name == "Brian"

    node = crud.get_node(db_session, 99)
    assert not node


def test_get_node_by_name(db_session):
    node = crud.get_node_by_name(db_session, "Cindy")
    assert node.name == "Cindy"


def test_get_nodes(db_session):
    nodes = crud.get_nodes(db_session)
    assert len(nodes) == 15


def test_get_node_like_name(db_session):
    nodes = crud.get_nodes_like_name(db_session, like="engineer")
    assert len(nodes) == 2
    chief = nodes[0]
    assert chief.name == "Chief Engineer"


def test_update_node(db_session):
    node = crud.update_node(db_session, 1, updated_name="Andy")
    assert node.name == "Andy"


def test_update_nonexistent_node(db_session):
    node = crud.update_node(db_session, 99, updated_name="Bogie Man")
    assert node is None


def test_delete_existing_node(db_session):
    orig_count = crud.get_table_size(db_session, models.Node)

    rows_deleted = crud.delete_node(db_session, 2)
    assert rows_deleted == 1
    node = crud.get_node(db_session, 2)
    assert node is None

    new_count = crud.get_table_size(db_session, models.Node)
    assert new_count == orig_count - 1


def test_delete_nonexistent_node(db_session):
    orig_count = crud.get_table_size(db_session, models.Node)

    rows_deleted = crud.delete_node(db_session, 99)
    assert rows_deleted == 0

    new_count = crud.get_table_size(db_session, models.Node)
    assert new_count == orig_count


def test_cant_create_duplicate_node_name(db_session):
    orig_count = crud.get_table_size(db_session, models.Node)

    node_1 = crud.get_node(db_session, 1)
    node_1_name: str = node_1.name

    new_node = crud.create_node(db_session, NodeCreate(name=node_1_name.upper()))
    new_count = crud.get_table_size(db_session, models.Node)

    assert orig_count == new_count
    assert new_node.id == node_1.id
    assert new_node.name == node_1_name


def test_create_node_name_substring(db_session):
    """
    Test that we can create two unique nodes where one node name is a substring of the other
    """
    david = crud.create_node(db_session, NodeCreate(name="David"))
    david_anthony = crud.create_node(db_session, NodeCreate(name="David Anthony"))

    assert david.id != david_anthony.id

    stephen_robert = crud.create_node(db_session, NodeCreate(name="Stephen Robert"))
    stephen = crud.create_node(db_session, NodeCreate(name="Stephen"))

    assert stephen.id != stephen_robert.id


def test_delete_all_nodes(db_session):
    original_node_count = crud.get_table_size(db_session, models.Node)
    assert original_node_count > 0

    crud.delete_nodes(db_session)

    new_node_count = crud.get_table_size(db_session, models.Node)
    assert new_node_count == 0
