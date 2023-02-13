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
    # Get the JSON-LD object from the submitted request
    s_json_ld_obj = await submitted_json_ld.json()

    # Create a graph to parse the JSON-LD data
    graph = Graph()

    # Get the content type from the request headers
    content_type = submitted_json_ld.headers['Content-Type']

    # Check if the content type is one of the accepted content types
    if content_type in ACCEPTED_CONTENT_TYPES:

        # Parse the JSON-LD data into the graph
        graph.parse(data=s_json_ld_obj, format=content_type)

        # Serialize the graph as Turtle text
        text_turtle = graph.serialize(format='text/turtle')

        # Create a database connection
        conn = db.create_sqlite3_connection(settings.data_db_file)
        with conn:
            # Create a new record for the inbox
            record = (
                str(uuid.uuid4()), datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f"), submitted_json_ld.client.host, json.dumps(s_json_ld_obj),
                text_turtle);
            # Insert the record into the inbox database
            record_id = db.create_inbox_record(conn, record)
            # Return a JSON response with a 201 Created status code and the record ID
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=record_id, headers=headers(record_id))
    else:
        # Return a 401 Unauthorized status code if the content type is not accepted
        return 401

    # Return a 201 Created status code
    return 201
