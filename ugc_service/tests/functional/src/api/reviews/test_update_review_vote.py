import pytest

endpoint_url = '/reviews/{review_id}/votes/{user_id}'
endpoint_method = 'put'


def test_correct_authenticated_request_updates_a_vote_with_code_200():
    pytest.fail()


def test_vote_update_is_reflected_in_a_corresponding_review():
    pytest.fail()


def test_unauthenticated_request_results_in_error_401():
    pytest.fail()


def test_unauthorized_request_results_in_error_403():
    pytest.fail()


def test_request_for_a_nonexistent_vote_results_in_error_404():
    pytest.fail()


def test_request_for_invalid_vote_id_results_in_error_422():
    pytest.fail()


def test_request_with_invalid_schema_results_in_error_422():
    pytest.fail()
