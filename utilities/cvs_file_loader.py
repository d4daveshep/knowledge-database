from datetime import datetime, date
from io import TextIOWrapper

import pandas as pd
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from web_apps import crud
from web_apps.schemas import NodeCreate, ConnectionCreate


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
    staff_data = StaffData(name=data[0].strip(), gm=data[1].strip(), employment=data[2].strip())
    # print(staff_data)
    return staff_data


def load_staff_list_from_csv_buffer(db_session: Session, buffer: TextIOWrapper) -> int:
    lines_processed = 0
    for _ in range(9):
        line = buffer.readline()
    while line:
        staff_data: StaffData = parse_staff_list_line(line)
        if staff_data.name == "" or staff_data.gm == "" or staff_data.employment == "":
            # print(f"blanks at {lines_processed}: {staff_data.json()}")
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


def load_time_by_task(db_session: Session, csv_filename: str) -> int:
    df = pd.read_csv(csv_filename, usecols=[0, 2, 5], header=0)
    lines_processed = len(df)

    worked_on = df.drop(columns=["[Job] Name"]).drop_duplicates()
    for row in worked_on.itertuples(index=False):
        crud.create_connection(db_session, ConnectionCreate(name="worked on", subject=NodeCreate(name=row[1]),
                                                            target=NodeCreate(name=row[0])))

    billed_to = df.drop(columns=["[Job] Client"]).drop_duplicates()
    for row in billed_to.itertuples(index=False):
        crud.create_connection(db_session, ConnectionCreate(name="worked on", subject=NodeCreate(name=row[1]),
                                                            target=NodeCreate(name=row[0])))

    has_job = df.drop(columns=["[Staff] Name"]).drop_duplicates()
    for row in has_job.itertuples(index=False):
        crud.create_connection(db_session, ConnectionCreate(name="worked on", subject=NodeCreate(name=row[0]),
                                                            target=NodeCreate(name=row[1])))

    return lines_processed


def parse_time_by_task_line(line) -> TaskTimeData:
    data = line.strip().split(',')
    time_task_data = TaskTimeData(client_name=data[0], job_name=data[2], staff_name=data[5], date=data[7],
                                  hours=data[9])
    # print(time_task_data)
    return time_task_data
