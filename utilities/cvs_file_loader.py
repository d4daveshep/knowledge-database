from pydantic import BaseModel
from sqlalchemy.orm import Session

from sql_app import crud
from sql_app.schemas import NodeCreate, ConnectionCreate


class StaffData(BaseModel):
    name: str
    gm: str
    employment: str


def parse_staff_list_line(line) -> StaffData:
    data = line.strip().split(',')
    return StaffData(name=data[0], gm=data[1], employment=data[2])


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
