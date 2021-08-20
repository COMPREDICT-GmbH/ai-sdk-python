import json

import pytest
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from compredict.exceptions import ClientError
from compredict.resources import Task, Algorithm


@pytest.mark.parametrize("callback,expected",
                         [
                             (['firstandtheend/last', 'lifeissupereasy', 'on/island/of/trees'],
                              "firstandtheend/last|lifeissupereasy|on/island/of/trees"),
                             (['we/wrote2/in/symbols', 'somestateandthe/other'],
                              "we/wrote2/in/symbols|somestateandthe/other"),
                             ('just/a/string', 'just/a/string')
                         ])
def test_set_callback_urls(api_client, callback, expected):
    actual = api_client.set_callback_urls(callback)
    assert actual == expected


@pytest.mark.parametrize("option, expected",
                         [
                             (False, False),
                             (True, True)
                         ])
def test_fail_on_error_and_verify_peer(api_client, option, expected):
    api_client.fail_on_error(option)
    api_client.verify_peer(option)

    assert api_client.connection.fail_on_error == expected
    assert api_client.connection.ssl == expected


def test_last_error(api_client, response, mocker, connection, content):
    mocker.patch('requests.get', return_value=response)
    response = connection.GET(endpoint="some/endpoint")
    actual_last_error = api_client.last_error
    # error = Error(response=content, status_code=400)

    assert actual_last_error == True
    assert response == False


def test_run_algorithm(api_client):
    algorithm_id = "id"
    data = {"data": "some_data"}
    callback_url = ["1callback", "2callback"]
    callback_param = [{1: "first"}, {2: "second"}]

    api_client.run_algorithm(algorithm_id=algorithm_id, data=data, callback_url=callback_url,
                             callback_param=callback_param)


def test_run_algorithm_with_client_error(mocker, api_client, response_400):
    algorithm_id = "id"
    data = {"data": "some_data"}
    callback_url = ["1callback", "2callback", "3callback"]
    callback_param = [{1: "first"}, {2: "second"}]

    mocker.patch('builtins.dict', side_effect=AttributeError)

    with pytest.raises(ClientError):
        api_client.run_algorithm(algorithm_id=algorithm_id, data=data, callback_url=callback_url,
                                 callback_param=callback_param)


def test_map_resource_with_error_raised(api_client):
    resource = "Tassk"
    object = {"version": "0.0.1"}

    with pytest.raises(ImportError):
        api_client._api__map_resource(resource, object)


def test_map_resource_with_task(api_client, object):
    resource = "Task"

    instance = api_client._api__map_resource(resource, object)

    assert isinstance(instance, Task)


def test_map_resource_with_algorithm(api_client):
    resource = "Algorithm"
    algorithm = {
        "id": "23",
        "versions": [{'version': '9.4.6'}]
    }
    instance = api_client._api__map_resource(resource, algorithm)

    assert isinstance(instance, Algorithm)


def test_map_collection_with_raising_error(api_client, object):
    resource = 'WrongName'
    objects = [object, object]

    with pytest.raises(ImportError):
        api_client._api__map_collection(resource, objects)


def test_map_collection(api_client, object):
    resource = "Task"
    objects = [object, object]

    results = api_client._api__map_collection(resource, objects)

    for result in results:
        assert isinstance(result, Task)


def test_process_data_with_value_error(api_client, data):
    content_type = "text/html"

    with pytest.raises(ValueError):
        api_client._api__process_data(content_type, data)


def test_write_json_file(api_client, data, mocker):
    content_type = "application/json"

    temp_file = mocker.patch('tempfile.NamedTemporaryFile')
    mocked = mocker.patch('compredict.client.api.__write_json_file')

    file, actual_content_type, bool = api_client._api__process_data(content_type, data)

    assert file == temp_file
    assert mocked.called == True
    assert actual_content_type == content_type
    assert bool == True


def test_RSA_decrypt_and_encrypt_with_error_raised(api_client):
    encrypted_key = json.dumps("dsfsdgryertn6435fsdf").encode('utf-8')
    data = "Some data to be encrypted"
    api_client.rsa_key = None

    with pytest.raises(Exception):
        api_client.RSA_decrypt(encrypted_key)
        api_client.RSA_encrypt(data)


def test_RSA_encrypt_and_decrypt(api_client):
    data = "here there is some data to be encrypted"

    result = api_client.RSA_encrypt(data)
    decrypted_msg = api_client.RSA_decrypt(result)

    assert data != result
    assert len(result) > len(data)
    assert data == decrypted_msg
