import pytest

endpoint_url = '/reviews/{review_id}/votes/'
endpoint_method = 'post'


def test_correct_authenticated_request_creates_and_returns_a_vote_with_code_201():
    pytest.fail()


def test_vote_creation_is_reflected_in_a_corresponding_review():
    pytest.fail()


def test_unauthenticated_request_results_in_error_401():
    pytest.fail()


def test_attempt_to_create_already_existing_vote_results_in_error_409():
    pytest.fail()


def test_request_with_invalid_schema_results_in_error_422():
    pytest.fail()
