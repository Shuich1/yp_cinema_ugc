import pytest

endpoint_url = '/ratings/{film_id}/{user_id}'
endpoint_method = 'get'


def test_correct_request_returns_a_rating_with_code_200():
    pytest.fail()


def test_request_for_a_nonexistent_rating_results_in_error_404():
    pytest.fail()


def test_request_for_invalid_rating_id_results_in_error_422():
    pytest.fail()
