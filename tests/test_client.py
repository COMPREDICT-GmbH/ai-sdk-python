import pytest

from compredict.exceptions import Error


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

# def test_run_algorithm(api_client):
#     algorithm_id = "id"
#     data= {"data" : "some_data"}
#     callback_url= ["1callback", "2callback"]
#     callback_param = [{1:"first"}, {2:"second"}]
#
#     run = api_client.run_algorithm(algorithm_id=algorithm_id, data=data, callback_url=callback_url, callback_param=callback_param)






