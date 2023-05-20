from datetime import datetime, date

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
    hours: int

    @validator("date", pre=True)
    def parse_date(cls, value):
        # custom validator to parse date string in format dd-mmm-yy
        return datetime.strptime(
            value,
            "%d-%b-%y"
        ).date()


def parse_staff_list_line(line) -> StaffData:
    data = line.strip().split(',')
    return StaffData(name=data[0], gm=data[1], employment=data[2])


8


def parse_time_by_task_line(line) -> TaskTimeData:
    data = line.strip().split(',')
    return TaskTimeData(client_name=data[0], job_name=data[2], staff_name=data[5], date=data[7], hours=data[9])


def load_staff_list(db_session: Session, csv_filename: str) -> int:
    lines_processed = 0
    with open(csv_filename) as csv_file:
        for _ in range(9):
            line = csv_file.readline()
        while line:
            staff_data: StaffData = parse_staff_list_line(line)
            if staff_data.name == "" or staff_data.gm == "" or staff_data.employment == "":
                line = csv_file.readline()
                continue
            crud.create_connection(db_session,
                                   ConnectionCreate(name="Under GM",
                                                    subject=NodeCreate(name=staff_data.name),
                                                    target=NodeCreate(name=staff_data.gm)
                                                    )
                                   )
            crud.create_connection(db_session,
                                   ConnectionCreate(name="Employment type",
                                                    subject=NodeCreate(name=staff_data.name),
                                                    target=NodeCreate(name=staff_data.employment)
                                                    )
                                   )

            lines_processed += 1
            line = csv_file.readline()

    return lines_processed
