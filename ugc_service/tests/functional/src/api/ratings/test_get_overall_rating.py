import pytest

endpoint_url = '/ratings/getOverallRating'
endpoint_method = 'get'


def test_correct_request_returns_an_overall_rating_with_code_200():
    pytest.fail()


def test_request_for_a_nonexistent_film_results_in_error_404():
    pytest.fail()


def test_request_for_a_film_without_ratings_results_in_error_404():
    pytest.fail()


def test_request_for_invalid_film_id_results_in_error_422():
    pytest.fail()
