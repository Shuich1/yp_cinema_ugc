from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Rating
from utils import write_to_db

endpoint_url = '/ratings/getOverallRating'
endpoint_method = 'get'


@pytest.mark.parametrize(['ratings_count'], [(10,), (1,)])
def test_correct_request_returns_an_overall_rating_with_code_200(
        db,
        api_request,
        ratings_count,
):
    film_id = uuid4()

    relevant_ratings = [Rating(film_id=film_id) for _ in range(ratings_count)]
    total_rating = sum(rating.rating for rating in relevant_ratings)
    avg_rating = round(total_rating / ratings_count, 1)

    ratings = relevant_ratings + [Rating() for _ in range(10)]

    write_to_db(db.ratings, *ratings)

    response = api_request(
        endpoint_method,
        endpoint_url,
        params={'film_id': film_id},
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_overall_rating = response_body['overall_rating']
    response_avg_rating = response_overall_rating['avg_rating']
    response_ratings_count = response_overall_rating['ratings_count']

    assert response_avg_rating == avg_rating
    assert response_ratings_count == ratings_count


def test_request_for_a_film_without_ratings_results_in_error_404(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url,
        params={'film_id': uuid4()},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_request_for_invalid_film_id_results_in_error_422(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url,
        params={'film_id': 'invalid'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
