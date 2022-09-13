import logging

import json

from dynaconf import Dynaconf


settings = Dynaconf(settings_files=["conf/settings.toml", "conf/.secrets.toml"],
                    environments=True)

ACCEPTED_CONTENT_TYPES = ['application/ld+json', 'json-ld',
                          'application/ld+json; profile="http://www.w3.org/ns/activitystreams"', 'turtle',
                          'text/turtle']

logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL,
                    format=settings.LOG_FORMAT)

data = {}


def headers(id):
    hdr = {'X-Powered-By': 'https://github.com/ekoi/dans-inbox',
           'Allow': 'GET, HEAD, POST',
           'Link': '<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type", <http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type"',
           'Location': 'https://dans-inbox.dataverse.tk/inbox/' + id}
    return hdr

