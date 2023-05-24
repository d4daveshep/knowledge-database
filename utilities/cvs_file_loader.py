from datetime import datetime, date
from io import TextIOWrapper

from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from sql_app import crud
from sql_app.schemas import NodeCreate, ConnectionCreate


class StaffData(BaseModel):
    name: str
    gm: str
    employment: str


class TaskTimeData(BaseModel):
    client_name: str
    job_name: str
    staff_name: str
    date: date
    hours: int | float

    @validator("date", pre=True)
    def parse_date(cls, value):
        # custom validator to parse date string in format dd-mmm-yy
        return datetime.strptime(
            value,
            "%d-%b-%y"
        ).date()


def parse_staff_list_line(line) -> StaffData:
    data = line.strip().split(',')
    staff_data = StaffData(name=data[0], gm=data[1], employment=data[2])
    # print(staff_data)
    return staff_data


def load_time_by_task(db_session: Session, csv_filename: str) -> int:
    lines_processed = 0
    with open(csv_filename) as csv_file:
        for _ in range(2):
            line = csv_file.readline()
        while line:
            task_time_data: TaskTimeData = parse_time_by_task_line(line)

            crud.create_connection(
                db_session, ConnectionCreate(name="worked on", subject=NodeCreate(name=task_time_data.staff_name),
                                             target=NodeCreate(name=task_time_data.client_name))
            )
            crud.create_connection(
                db_session, ConnectionCreate(name="billed time to", subject=NodeCreate(name=task_time_data.staff_name),
                                             target=NodeCreate(name=task_time_data.job_name))
            )
            crud.create_connection(
                db_session, ConnectionCreate(name="has job", subject=NodeCreate(name=task_time_data.client_name),
                                             target=NodeCreate(name=task_time_data.job_name))
            )

            # a_graph.add_connection(name, "worked on", client)
            # a_graph.add_connection(name, "billed time to", job)
            # a_graph.add_connection(client, "has job", job)
            lines_processed += 1
            line = csv_file.readline()

    return lines_processed


def parse_time_by_task_line(line) -> TaskTimeData:
    data = line.strip().split(',')
    time_task_data = TaskTimeData(client_name=data[0], job_name=data[2], staff_name=data[5], date=data[7],
                                  hours=data[9])
    # print(time_task_data)
    return time_task_data


def load_staff_list_from_csv_buffer(db_session: Session, buffer: TextIOWrapper) -> int:
    lines_processed = 0
    for _ in range(9):
        line = buffer.readline()
    while line:
        staff_data: StaffData = parse_staff_list_line(line)
        if staff_data.name == "" or staff_data.gm == "" or staff_data.employment == "":
            line = buffer.readline()
            continue
        crud.create_connection(
            db_session, ConnectionCreate(name="Under GM",
                                         subject=NodeCreate(name=staff_data.name),
                                         target=NodeCreate(name=staff_data.gm)
                                         )
        )
        crud.create_connection(
            db_session, ConnectionCreate(name="Employment type",
                                         subject=NodeCreate(name=staff_data.name),
                                         target=NodeCreate(name=staff_data.employment)
                                         )
        )

        lines_processed += 1
        line = buffer.readline()

    return lines_processed


def load_staff_list_from_csv_file(db_session: Session, csv_filename: str) -> int:
    lines_processed = 0
    with open(csv_filename) as csv_file:
        lines_processed = load_staff_list_from_csv_buffer(db_session, csv_file)

    return lines_processed
