from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from web_apps import models, crud
from utilities.cvs_file_loader import load_staff_list_from_csv_file, parse_staff_list_line, StaffData, TaskTimeData, \
    parse_time_by_task_line, load_time_by_task


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://")#, echo=True)
    models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        # tests run

        # tear down
        pass


def test_parse_staff_list_line():
    data_line = "Aaron Ooi,Dan Cornwall,Contract,  40"
    staff_data: StaffData = parse_staff_list_line(data_line)
    assert staff_data.name == "Aaron Ooi"
    assert staff_data.gm == "Dan Cornwall"
    assert staff_data.employment == "Contract"


def test_load_staff_list(db_session):
    filename = "./Utilisation report - 20230227.xlsx - Staff List.csv"

    lines_processed = load_staff_list_from_csv_file(db_session, filename)
    assert lines_processed == 181

    assert crud.get_table_size(db_session, models.Connection) == 362
    assert crud.get_table_size(db_session, models.Node) == 188

    all_connections: list[models.Connection] = crud.get_connections(db_session, limit=400)
    assert len(all_connections) == 362

    aaron_connections: list[models.Connection] = crud.get_connections_to_node_like_name(db_session, like="Aaron Ooi")
    assert len(aaron_connections) == 2

    zoe_connections: list[models.Connection] = crud.get_connections_to_node_like_name(db_session, like="Zoe Xu")
    assert len(zoe_connections) == 2


def test_parse_time_by_task_line():
    data_line = "AlphaCert Limited,J003255,ALPH-2136 ACC AWS Discovery,AlphaCert Consultancy,AlphaCert Consultancy,Terence White,PERM,30-Jan-23,Yes,1,,Finalise and issue report,Terence White,Terence White"
    task_time_data: TaskTimeData = parse_time_by_task_line(data_line)

    assert task_time_data.client_name == "AlphaCert Limited"
    assert task_time_data.job_name == "ALPH-2136 ACC AWS Discovery"
    assert task_time_data.staff_name == "Terence White"
    assert task_time_data.date == date(2023, 1, 30)
    assert task_time_data.hours == 1

    data_line = "AlphaCert Limited,J003255,ALPH-2136 ACC AWS Discovery,AlphaCert Consultancy,AlphaCert Consultancy,Terence White,PERM,30-Jan-23,Yes,0.25,,Finalise and issue report,Terence White,Terence White"
    task_time_data: TaskTimeData = parse_time_by_task_line(data_line)
    assert task_time_data.hours == 0.25

def test_load_time_by_task(db_session):
    filename = "./Utilisation report - 20230227.xlsx - TimeByTask.csv"

    lines_processed = load_time_by_task(db_session, filename)
    assert lines_processed == 5056

    assert crud.get_table_size(db_session, models.Connection) == 1061
    assert crud.get_table_size(db_session, models.Node) == 382
