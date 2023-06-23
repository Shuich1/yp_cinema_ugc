import pytest

endpoint_url = '/reviews/'
endpoint_method = 'post'


def test_correct_authenticated_request_creates_and_returns_a_review_with_code_201():
    pytest.fail()


def test_unauthenticated_request_results_in_error_401():
    pytest.fail()


def test_request_with_invalid_schema_results_in_error_422():
    pytest.fail()
