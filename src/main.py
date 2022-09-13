import importlib.metadata as md
import logging

import uvicorn
from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.responses import JSONResponse

import db
from src import protected
from src.common import settings

__version__ = md.metadata("ldn-inbox-service")["version"]


log = logging.getLogger(__name__)

api_keys = [
    settings.LDN_INBOX_SERVICE_API_KEY
]  # Todo: This is encrypted in the .secrets.toml

#Authorization Form: It doesn't matter what you type in the form, it won't work yet. But we'll get there.
#See: https://fastapi.tiangolo.com/tutorial/security/first-steps/
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


app = FastAPI(title=settings.FASTAPI_TITLE, description=md.metadata("ldn-inbox-service")["description"],
              version=__version__)

app.include_router(
    protected.router,
    tags=["Protected"],
    prefix="",
    dependencies=[Depends(api_key_auth)]
)


@app.head("/")
@app.get('/')
def about(response: Response):
    response.headers['X-Powered-By'] = 'https://github.com/ekoi/dans-inbox'
    # response.headers[
    #     'Link'] = '<' + 'http://localhost:1012/inbox' + '>; rel="http://www.w3.org/ns/ldp#inbox", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'
    response.headers['Allow'] = "GET, HEAD, POST"
    response.headers[
        'Link'] = '<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type", <http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'
    response.headers['Accept-Post'] = 'application/ld+json, text/turtle'
    return 'PoC Inbox'


@app.get('/inbox')
def get_inbox():
    content = db.select_all_inboxes(settings.data_db_file)
    # return JSONResponse(content={"eko":"test"}, headers=headers)
    return JSONResponse(status_code=200, content=content)


@app.get('/inbox/{id}')
def get_inbox(id: str):

    content = db.select_inbox_by_id(settings.data_db_file, id)
    # return JSONResponse(content={"eko":"test"}, headers=headers)
    return JSONResponse(status_code=200, content=content)

@app.get('/version')
def version():
    return __version__





if __name__ == "__main__":
    if settings.current_env == "DOCKER":  # this is the initial default
        print('name: ', settings.NAME)
    print('data_db_file', settings.data_db_file)
    print(settings.ROOT_PATH_FOR_DYNACONF)

    sql_create_inbox_table = """ CREATE TABLE `inbox` (`id` uuid,`created_time` datetime,`updated_time` datetime,
                                    `deleted_time` datetime,`sender` text,`payload` blob, `payload_turtle` text,`valid_rdf` numeric,PRIMARY KEY (`id`));"""
    #todo: if not found, creates one.

    # create a database connection
    conn = db.create_sqlite3_connection(settings.data_db_file)

    # create tables
    if conn is not None:
        # create inbox table
        db.create_table(conn, sql_create_inbox_table)
    else:
        print("Error! cannot create the database connection.")

    uvicorn.run(app, host="0.0.0.0", port=1210)
    # uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)

# curl -D - -X POST -H "Content-Type: application/ld+json" -d @json-ld-example.json  http://localhost/inbox
# curl -i -X POST -d '<eko> <works> <DANS> .' -H'Content-Type: text/turtle'  http://127.0.0.1:1012/inbox
