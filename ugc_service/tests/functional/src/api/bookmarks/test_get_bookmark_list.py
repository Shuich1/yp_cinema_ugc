import pytest

endpoint_url = '/bookmarks/'
endpoint_method = 'get'


def test_correct_request_returns_a_list_of_bookmarks_with_code_200():
    pytest.fail()


def test_request_for_nonexistent_user_id_returns_an_empty_list_with_code_200():
    pytest.fail()


def test_request_for_invalid_user_id_results_in_error_422():
    pytest.fail()
