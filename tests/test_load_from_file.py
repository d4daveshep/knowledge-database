import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sql_app import models, crud
from utilities.cvs_file_loader import load_staff_list, parse_staff_list_line, StaffData


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", echo=True)

    models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass


def test_parse_staff_list_line():
    data_line = "Aaron Ooi,Dan Cornwall,Contract,  40"
    staff_data: StaffData = parse_staff_list_line(data_line)
    assert staff_data.name == "Aaron Ooi"
    assert staff_data.gm == "Dan Cornwall"
    assert staff_data.employment == "Contract"


def test_load_staff_list(db_session):
    filename = "./Utilisation report - 20230227.xlsx - Staff List.csv"

    lines_processed = load_staff_list(db_session, filename)
    assert lines_processed == 181

    all_connections: list[models.Connection] = crud.get_connections(db_session, limit=400)
    assert len(all_connections) == 362

    aaron_connections: list[models.Connection] = crud.get_connections_to_node_like_name(db_session, like="Aaron Ooi")
    assert len(aaron_connections) == 2

    zoe_connections: list[models.Connection] = crud.get_connections_to_node_like_name(db_session, like="Zoe Xu")
    assert len(zoe_connections) == 2




