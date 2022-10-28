import json

import pytest

from compredict.exceptions import ClientError, ServerError
from compredict.resources import Task, Algorithm, Version


@pytest.mark.parametrize("callback,expected",
                         [
                             (['firstandtheend/last', 'lifeissupereasy', 'on/island/of/trees'],
                              "firstandtheend/last|lifeissupereasy|on/island/of/trees"),
                             (['we/wrote2/in/symbols', 'somestateandthe/other'],
                              "we/wrote2/in/symbols|somestateandthe/other"),
                             ('just/a/string', 'just/a/string')
                         ])
def test_set_callback_urls(api_client, callback, expected):
    actual = api_client._set_callback_urls(callback)

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


def test_last_error(response_400, mocker, connection):
    mocker.patch('requests.get', return_value=response_400)
    connection.GET(endpoint="some/endpoint")

    actual_last_error = connection.last_error

    assert actual_last_error


def test_run_algorithm(api_client, mocker, response_200):
    algorithm_id = "id"
    data = {"data": "some_data"}
    callback_url = ["1callback", "2callback"]
    callback_param = [{1: "first"}, {2: "second"}]

    mocker.patch('requests.post', return_value=response_200)

    response = api_client.run_algorithm(algorithm_id=algorithm_id, data=data,
                                        callback_url=callback_url,
                                        callback_param=callback_param)

    assert response.error == 'False'
    assert response.result == "some result"


def test_run_algorithm_with_type_error(mocker, api_client):
    algorithm_id = "id"
    data = {"data": "some_data"}
    callback_url = ["1callback", "2callback", "3callback"]
    callback_param = [{1: "first"}, {2: "second"}]
    mocker.patch('builtins.dict', side_effect=AttributeError)

    with pytest.raises(TypeError):
        api_client.run_algorithm(algorithm_id=algorithm_id, data=data, callback_url=callback_url,
                                 callback_param=callback_param)


def test_run_algorithm_with_client_error(mocker, api_client, response_400):
    api_client.connection.fail_on_error = True
    algorithm_id = "algorithm-slug"
    data = {"data": "some_data"}
    mocker.patch('requests.post', return_value=response_400)

    with pytest.raises(ClientError):
        api_client.run_algorithm(algorithm_id=algorithm_id, data=data)


def test_run_algorithm_with_server_error(mocker, api_client):
    algorithm_id = "id"
    data = {"data": "some_data"}
    mocker.patch('compredict.connection.Connection.handle_response', side_effect=ServerError)

    with pytest.raises(ServerError):
        api_client.run_algorithm(algorithm_id=algorithm_id, data=data)


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


def test_RSA_decrypt_and_encrypt_with_error_raised(api_client):
    encrypted_key = json.dumps("dsfsdgryertn6435fsdf").encode('utf-8')
    data = "Some data to be encrypted"

    api_client.rsa_key = None

    with pytest.raises(Exception):
        api_client.RSA_decrypt(encrypted_key)
        api_client.RSA_encrypt(data)


def test_RSA_encrypt_and_decrypt(api_client, rsa_key):
    data = "here there is some data to be encrypted"

    api_client.rsa_key = rsa_key
    result = api_client.RSA_encrypt(data)
    decrypted_msg = api_client.RSA_decrypt(result)

    assert data != result
    assert len(result) > len(data)
    assert data == decrypted_msg


def test_build_get_arguments(api_client):
    type = "input"
    version = "1.2.2"
    expected = "?type=input&version=1.2.2"

    actual = api_client._api__build_get_args(type=type, version=version)

    assert actual == expected


def test_get_task_results(api_client, mocker, response_200_with_result):
    task_id = '12jffd'
    mocker.patch('requests.get', return_value=response_200_with_result)

    response = api_client.get_task_results(task_id)

    assert isinstance(response, Task)
    assert response.reference == task_id


def test_get_algorithm_versions(api_client, mocker, response_200_with_versions):
    algorithm_id = 'mass_estimation'
    mocker.patch('requests.get', return_value=response_200_with_versions)

    response = api_client.get_algorithm_versions(algorithm_id)

    assert isinstance(response[0], Version)
    assert isinstance(response[1], Version)


def test_get_algorithm_version(api_client, mocker, response_200_with_version):
    algorithm_id = 'co2_emission'
    version = '1.3.0'
    mocker.patch('requests.get', return_value=response_200_with_version)

    response = api_client.get_algorithm_version(algorithm_id, version)

    assert isinstance(response, Version)
    assert response.version == version


def test_get_template(api_client, mocker, response_200_with_url):
    algorithm_id = 'algorithm'
    mocker.patch('requests.get', return_value=response_200_with_url)
    mocker.patch('tempfile._TemporaryFileWrapper')

    file = api_client.get_template(algorithm_id)

    assert file.write.called is True
    assert file.seek.called is True


def test_get_graph(api_client, mocker, response_200_with_url):
    algorithm_id = 'another_algorithm'
    mocker.patch('requests.get', return_value=response_200_with_url)
    mocker.patch('tempfile._TemporaryFileWrapper')

    file = api_client.get_graph(algorithm_id=algorithm_id, file_type='input')

    assert file.write.called is True
    assert file.seek.called is True


def test_get_algorithm(api_client, response_200_with_algorithm, mocker):
    algorithm_id = 'another_algorithm'
    mocker.patch('requests.get', return_value=response_200_with_algorithm)

    response = api_client.get_algorithm(algorithm_id)

    assert isinstance(response, Algorithm)


def test_get_algorithms(api_client, response_200_with_algorithms, mocker):
    mocker.patch('requests.get', return_value=response_200_with_algorithms)

    responses = api_client.get_algorithms()

    for response in responses:
        assert isinstance(response, Algorithm)


def test_process_evaluate_with_dict(api_client):
    evaluate_param = {
        'feature': 'evaluation'
    }

    evaluation = api_client._api__process_evaluate(evaluate_param)
    expected = '{"feature": "evaluation"}'
    assert evaluation == expected


def test_cancel_task(api_client, mocker, response_202_cancelled_task):
    task_id = '35f438fd-6c4d-42a1-8ad0-dfa8dbfcf5da'
    mocker.patch('requests.delete', return_value=response_202_cancelled_task)
    cancelled_task = api_client.cancel_task(task_id)
    assert isinstance(cancelled_task, Task)


def test_printing_error(mocker, api_client):
    algorithm_id = "id"
    data = {"data": "some_data"}
    mocker.patch('compredict.connection.Connection.handle_response',
                 side_effect=ServerError("This is error that is going to be printed"))

    try:
        api_client.run_algorithm(algorithm_id=algorithm_id, data=data)
    except ServerError as e:
        print(e)
        assert repr(e) == "This is error that is going to be printed"


def test_train_algorithm(mocker, api_client, response_200_with_job_id):
    algorithm_id = "algorithm-slug"
    data = {"data": "some_data"}
    mocker.patch('requests.post', return_value=response_200_with_job_id)
    result_task = api_client.train_algorithm(algorithm_id, data)
    assert isinstance(result_task, Task)
    assert result_task.job_id == "s1o2m3e4-jobid"


def test_train_algorithm_with_client_error(mocker, api_client, response_400):
    api_client.connection.fail_on_error = True
    algorithm_id = "trainable-algorithm"
    data = {"data": "some_data"}
    mocker.patch('requests.post', return_value=response_400)

    with pytest.raises(ClientError):
        api_client.train_algorithm(algorithm_id=algorithm_id, data=data, export_new_version=True)


def test_train_algorithm_with_server_error(mocker, api_client):
    algorithm_id = "trainable-algorithm"
    data = {"data": "some_data"}
    mocker.patch('compredict.connection.Connection.handle_response', side_effect=ServerError)

    with pytest.raises(ServerError):
        api_client.train_algorithm(algorithm_id=algorithm_id, data=data, export_new_version=True)


def test_generate_token(api_client, mocker, response_200_with_tokens_generated):
    mocker.patch('requests.post', return_value=response_200_with_tokens_generated)
    api_client.generate_token(username="someuser", password="andpassword")
    assert api_client.token == "sometokenvalue"
    assert api_client.token_refresh == "somerefreshtokenvalue"


def test_generete_token_with_error(api_client, mocker, response_400_with_credentials_error):
    mocker.patch('requests.post', return_value=response_400_with_credentials_error)
    with pytest.raises(ClientError) as excinfo:
        api_client.generate_token(username="user", password="somepass")
    assert 'errors' in str(excinfo.value)


def test_refresh_token(api_client, mocker, response_200_with_refreshed_token):
    mocker.patch('requests.post', return_value=response_200_with_refreshed_token)
    api_client.refresh_token('refresh_token')
    assert api_client.token == 'refreshedtoken'


def test_refresh_token_with_error(api_client, mocker, response_400_with_wrong_refresh_token):
    mocker.patch('requests.post', return_value=response_400_with_wrong_refresh_token)
    with pytest.raises(ClientError) as excinfo:
        api_client.refresh_token('token_to_refresh')
    assert 'errors' in str(excinfo.value)


def test_verify_token(api_client, mocker, response_200_token_verified):
    mocker.patch('requests.post', return_value=response_200_token_verified)
    assert api_client.verify_token('sometoken')


def test_verify_with_error(api_client, mocker, response_429_throttling_error):
    mocker.patch('requests.post', return_value=response_429_throttling_error)
    with pytest.raises(ClientError) as excinfo:
        api_client.verify_token('someothertoken')
    assert 'error' in str(excinfo.value)
