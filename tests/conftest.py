import json

import pytest
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from requests import Response

from compredict.client import api
from compredict.connection import Connection
from compredict.resources import Task


@pytest.fixture(scope='session')
def rsa_key():
    generated_key = RSA.generate(1024)
    rsa_key = PKCS1_OAEP.new(generated_key)
    return rsa_key


@pytest.fixture(scope='session')
def api_client(rsa_key):
    api_client = api.get_instance()
    api_client.rsa_key = rsa_key
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
def response_200_with_url(successful_content):
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


@pytest.fixture(scope='module')
def task():
    task = Task()
    return task


@pytest.fixture(scope='module')
def object():
    object = {
        "status": "In Progress"
    }
    return object


@pytest.fixture(scope='module')
def data():
    data = {"1": [346.5, 6456.6, 56.7], "2": [343.4, 34.6, 45.7]}
    return data
