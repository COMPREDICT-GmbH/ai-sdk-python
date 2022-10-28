import pytest

from compredict.utils.utils import adjust_file_name_to_content_type, extract_error_message


@pytest.mark.parametrize(
    "content_type, features_name",
    [
        ("application/json", "features.json"),
        ("application/parquet", "features.parquet"),
        ("text/csv", "features.csv")
    ]
)
def test_adjust_file_name_to_content_type(content_type, features_name):
    assert adjust_file_name_to_content_type(content_type) == features_name


def test_extract_error_message():
    text = "Exception Value: name 'DataFormatError' is not defined " \
           "Request information:"
    assert extract_error_message(text) == "name 'DataFormatError' is not defined"


def test_extract_error_message_when_key_words_not_found():
    text = 'Some other text with Exception, but without' \
           'right key words'
    assert extract_error_message(text) == "Internal Server Error"
