import datetime
from io import BytesIO, TextIOWrapper
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import utilities
from utilities.cvs_file_loader import load_staff_list_from_csv_buffer
from utilities.load_test_data import load_test_data
from . import models, crud
from .crud import get_connection_names
from .database import LocalSession, engine
from .json_rest_app import get_node, get_nodes, get_connections, create_connection, delete_all_nodes, \
    get_database_stats, get_connection
from .schemas import NodeCreate, ConnectionCreate, Connection

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Dependency
def get_db_session():
    db_session = LocalSession()
    try:
        yield db_session
    finally:
        db_session.close()


@app.get('/', response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})


@app.get("/file-upload", response_class=HTMLResponse)
def file_upload_page(request: Request):
    return templates.TemplateResponse("file-upload.html", {"request": request})


@app.post('/upload')
def upload(file: UploadFile = File(...), db_session: Session = Depends(get_db_session)):
    try:
        file_contents = file.file.read()
        text_buffer = TextIOWrapper(BytesIO(file_contents))
        lines_processed = load_staff_list_from_csv_buffer(db_session, text_buffer)
    except:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        text_buffer.close()
        file.file.close()

    return {"message": "OK", "lines processed": lines_processed}

    # remove a column from the DataFrame
    # df.drop('age', axis=1, inplace=True)
    #
    # headers = {'Content-Disposition': 'attachment; filename="modified_data.csv"'}
    # return Response(df.to_csv(), headers=headers, media_type='text/csv')


@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    date_string = datetime.date.today().strftime("%A %d %b %Y")
    return templates.TemplateResponse("home.html", {"request": request, "date": date_string})


@app.get("/connections-to-node/{node_id}", response_class=HTMLResponse)
def connection_results(request: Request, node_id: int, db_session: Session = Depends(get_db_session)):
    node = get_node(node_id=node_id, db_session=db_session)
    connections = get_connections(node_id=node_id, db_session=db_session)
    return templates.TemplateResponse("connections-to-node-results.html",
                                      {"request": request, "node": node, "connections": connections})


@app.get("/add-connection", response_class=HTMLResponse)
def add_new_connection(request: Request, connection: Connection = None):
    return templates.TemplateResponse("add-connection.html", {"request": request, "connection": connection})


@app.post("/add-connection", response_class=HTMLResponse)
def create_connection_in_database(request: Request, subject: str = Form(), conn_name: str = Form(),
                                  target: str = Form(), db_session: Session = Depends(get_db_session)):
    connection = ConnectionCreate(subject=NodeCreate(name=subject), name=conn_name, target=NodeCreate(name=target))

    connection = create_connection(db_session=db_session, connection=connection)
    return templates.TemplateResponse("/add-connection.html", {"request": request, "connection": connection})


@app.get("/purge-database", response_class=HTMLResponse)
def show_purge_database_page(request: Request):
    return templates.TemplateResponse("/purge-database.html", {"request": request})


@app.post("/purge-database", response_class=HTMLResponse)
def purge_database(request: Request, db_session: Session = Depends(get_db_session)):
    delete_all_nodes(db_session)
    stats = get_database_stats(db_session)
    return templates.TemplateResponse("/database-stats.html", {"request": request, "stats": stats})


@app.get("/database-stats", response_class=HTMLResponse)
def show_database_stats_page(request: Request, db_session: Session = Depends(get_db_session)):
    stats = get_database_stats(db_session)
    return templates.TemplateResponse("/database-stats.html", {"request": request, "stats": stats})


@app.get("/connections/", response_class=HTMLResponse)
def get_connections_by_name(request: Request, name_like: str, db_session: Session = Depends(get_db_session)):
    connections: list[Connection] = get_connections(name_like=name_like, db_session=db_session)

    return templates.TemplateResponse("/connection-results.html",
                                      {"request": request, "name_like": name_like, "connections": connections})


@app.get("/search", response_class=HTMLResponse)
def show_search_page(request: Request):
    return templates.TemplateResponse("/search.html", {"request": request})


@app.get("/search-results", response_class=HTMLResponse)
def search_results(request: Request, like: str, db_session: Session = Depends(get_db_session)):
    nodes = get_nodes(like=like, db_session=db_session)
    connection_names: dict[str:int] = get_connection_names(like=like, db_session=db_session)
    return templates.TemplateResponse("search-results.html", {"request": request, "like": like, "nodes": nodes,
                                                              "connection_names": connection_names})


@app.get("/load-test-data", response_class=HTMLResponse)
def show_load_test_data_page(request: Request):
    return templates.TemplateResponse("/load-test-data.html", {"request": request})


@app.post("/load-test-data", response_class=HTMLResponse)
def load_test_data(request: Request, db_session: Session = Depends(get_db_session)):
    utilities.load_test_data.load_test_data(db_session)

    stats = get_database_stats(db_session)
    return templates.TemplateResponse("/database-stats.html", {"request": request, "stats": stats})


@app.get("/delete-connection/{connection_id}", response_class=HTMLResponse)
def delete_connection(request: Request, connection_id: int, name_like: str,
                      db_session: Session = Depends(get_db_session)):
    if not crud.delete_connection(db_session, connection_id):
        raise HTTPException(status_code=404)

    connections: list[Connection] = get_connections(name_like=name_like, db_session=db_session)

    return templates.TemplateResponse("/connection-results.html",
                                      {"request": request, "name_like": name_like, "connections": connections})


@app.post("/delete-connections/", response_class=HTMLResponse)
def delete_connections(request: Request, name_like: str = Form(...),
                       conn_id: List[int] = Form(list()), db_session: Session = Depends(get_db_session)):
    """
    This handles a dynamic number of conn_id items in the form
    :param conn_id: list of connection ids to be deleted, can be empty
    """
    print(f"name_like={name_like}")
    print("conn_id list", conn_id)
    for id in conn_id:
        if not crud.delete_connection(db_session, connection_id=id):
            raise HTTPException(status_code=404)

    connections: list[Connection] = get_connections(name_like=name_like, db_session=db_session)

    return templates.TemplateResponse("/connection-results.html",
                                      {"request": request, "name_like": name_like, "connections": connections})


@app.get("/edit-connection/{connection_id}", response_class=HTMLResponse)
def show_edit_connection_page(request: Request, connection_id: int,
                              db_session: Session = Depends(get_db_session)):
    connection = get_connection(connection_id=connection_id, db_session=db_session)
    return templates.TemplateResponse("/edit-connection.html", {"request": request, "connection_name": connection.name})
