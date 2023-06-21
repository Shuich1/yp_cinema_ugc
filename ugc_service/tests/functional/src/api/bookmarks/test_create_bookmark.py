import pytest

endpoint_url = '/bookmarks/'
endpoint_method = 'post'


def test_correct_authenticated_request_creates_and_returns_a_bookmark_with_code_200():
    pytest.fail()


def test_unauthenticated_request_results_in_error_401():
    pytest.fail()


def test_attempt_to_create_already_existing_bookmark_results_in_error_409():
    pytest.fail()


def test_request_with_invalid_film_id_results_in_error_422():
    pytest.fail()
