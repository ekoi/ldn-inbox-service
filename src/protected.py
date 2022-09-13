import json
import uuid
from datetime import datetime

# import codecs
from fastapi import APIRouter, Request
from rdflib import Graph
from starlette import status
from starlette.responses import JSONResponse

from src import db
from src.common import ACCEPTED_CONTENT_TYPES, headers
from src.common import settings

router = APIRouter()


@router.get("/settings")
async def get_settings():
    return settings


@router.head("/inbox")
@router.post('/inbox')
async def post_inbox(submitted_json_ld: Request):
    s_json_ld_obj = await submitted_json_ld.json()
    graph = Graph()
    content_type = submitted_json_ld.headers['Content-Type']
    if content_type in ACCEPTED_CONTENT_TYPES:
        print(content_type)
        graph.parse(data=s_json_ld_obj, format=content_type)
        text_turtle = graph.serialize(format='text/turtle')
        # create a database connection
        conn = db.create_sqlite3_connection(settings.data_db_file)
        with conn:
            # create a new record
            record = (
                str(uuid.uuid4()), datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f"), submitted_json_ld.client.host, json.dumps(s_json_ld_obj),
                text_turtle);
            record_id = db.create_inbox_record(conn, record)
            print(record_id)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=record_id, headers=headers(record_id))
    else:
        return 401

    return 201
