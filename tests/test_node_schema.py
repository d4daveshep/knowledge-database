import pytest
from pydantic import ValidationError

from sql_app.schemas import NodeCreate, Node


def test_node_create():
    node = NodeCreate(name="first node")
    assert node.name == "first node"

    with pytest.raises(ValidationError) as err:
        NodeCreate()


def test_node():
    node_1 = Node(id=12, name="the node")
    assert node_1.id == 12

    with pytest.raises(ValidationError) as err:
        Node()

    with pytest.raises(ValidationError) as err:
        Node(id=12)

    with pytest.raises(ValidationError) as err:
        Node(name="missing id")
