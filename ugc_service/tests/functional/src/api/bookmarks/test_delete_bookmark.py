import pytest

endpoint_url = '/bookmarks/{film_id}/{user_id}/'
endpoint_method = 'delete'


def test_correct_authenticated_request_deletes_a_bookmark_with_code_204():
    pytest.fail()


def test_unauthenticated_request_results_in_error_401():
    pytest.fail()


def test_unauthorized_request_results_in_error_403():
    pytest.fail()


def test_request_for_a_nonexistent_bookmark_results_in_error_404():
    pytest.fail()


def test_request_for_invalid_film_id_results_in_error_422():
    pytest.fail()
