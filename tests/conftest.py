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
def unsucessful_content():
    unsucessful_content = {
        'error': "True",
        'error_msg': 'Bad request'

    }
    return unsucessful_content


@pytest.fixture(scope="module")
def successful_content():
    successful_content = {
        "error": "False",
        "result": "some result"
    }
    return successful_content


@pytest.fixture(scope="module")
def response_400(unsucessful_content):
    response = Response()
    response.status_code = 400
    response._content = json.dumps(unsucessful_content).encode('utf-8')
    return response


@pytest.fixture(scope="module")
def response_500(unsucessful_content):
    response = Response()
    response.status_code = 500
    response._content = json.dumps(unsucessful_content).encode('utf-8')
    return response


@pytest.fixture(scope="module")
def response_200(successful_content):
    response_200 = Response()
    response_200.status_code = 200
    response_200._content = json.dumps(successful_content).encode('utf-8')
    response_200.url = 'https://core.compredict.ai/api/v1/algorithms/56'
    response_200.headers['Content-Type'] = 'application/json'
    return response_200


@pytest.fixture(scope="module")
def response_200_with_url(successful_content, unsucessful_content):
    response_200_with_url = Response()
    response_200_with_url.status_code = 200
    response_200_with_url._content = json.dumps(successful_content).encode('utf-8')
    response_200_with_url.url = 'https://core.compredict.ai/api/v1/algorithms/56/graph'
    response_200_with_url.headers['Content-Type'] = 'image/png'
    return response_200_with_url


@pytest.fixture(scope='session')
def connection_with_fail_on_true():
    connection_with_fail_on_true = Connection(url="https://core.compredict.ai/api/")
    connection_with_fail_on_true.fail_on_error = True
    return connection_with_fail_on_true


@pytest.fixture(scope='session')
def connection():
    connection = Connection(url="https://core.compredict.ai/api/")
    return connection
