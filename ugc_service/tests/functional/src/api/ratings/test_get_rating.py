from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Rating
from utils import write_to_db

endpoint_url = '/ratings/{film_id}/{user_id}'
endpoint_method = 'get'


def test_correct_request_returns_a_rating_with_code_200(db, api_request):
    rating = Rating()

    write_to_db(db.ratings, rating)

    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=rating.film_id, user_id=rating.user_id),
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_rating = Rating.parse_obj(response_body['rating'])

    assert response_rating.id == rating.id


def test_request_for_a_nonexistent_rating_results_in_error_404(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=uuid4()),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ['film_id', 'user_id'],
    [(uuid4(), 'invalid'), ('invalid', uuid4())],
)
def test_request_for_invalid_rating_id_results_in_error_422(
        api_request,
        film_id,
        user_id,
):
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=film_id, user_id=user_id),
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
