import json

import pytest
from requests import Response

from compredict.client import api
from compredict.connection import Connection


@pytest.fixture(scope='session')
def api_client():
    api_client = api.get_instance()
    return api_client


@pytest.fixture(scope="module")
def content():
    content = {
        'error': "True",
        'error_msg': 'Bad request'

    }
    return content


@pytest.fixture(scope="module")
def response(content):
    response = Response()
    response.status_code = 400
    response._content = json.dumps(content).encode('utf-8')
    return response


@pytest.fixture(scope='session')
def connection():
    connection = Connection(url="https://core.compredict.ai/api/")
    return connection
