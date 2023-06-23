from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Rating
from utils import write_to_db, extract_from_db

endpoint_url = '/ratings/'
endpoint_method = 'post'


def test_correct_authenticated_request_creates_and_returns_a_rating_with_code_201(
        db,
        api_request,
):
    user_id = uuid4()
    rating = Rating(user_id=user_id)

    payload = {'film_id': str(rating.film_id), 'rating': rating.rating}
    response = api_request(
        endpoint_method,
        endpoint_url,
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.CREATED

    response_body = response.json()
    response_rating = Rating.parse_obj(response_body['rating'])

    search_params = rating.dict(exclude={'created', 'updated'})
    db_rating = extract_from_db(Rating, db.ratings, search_params)

    assert response_rating.id == db_rating.id


def test_unauthenticated_request_results_in_error_401(api_request):
    rating = Rating()

    payload = {'film_id': str(rating.film_id), 'rating': rating.rating}
    response = api_request(endpoint_method, endpoint_url, json=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_attempt_to_create_already_existing_rating_results_in_error_409(
        db,
        api_request,
):
    user_id = uuid4()
    rating = Rating(user_id=user_id)

    write_to_db(db.ratings, rating)

    payload = {'film_id': str(rating.film_id), 'rating': rating.rating}
    response = api_request(
        endpoint_method,
        endpoint_url,
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.parametrize(
    ['payload'],
    [
        ({'film_id': 'invalid', 'rating': 4},),
        ({'film_id': str(uuid4()), 'rating': 'invalid'},),
        ({'film_id': str(uuid4()), 'rating': -3},),
        ({'film_id': str(uuid4()), 'rating': 100},),
        ({'film_id': str(uuid4())}),
    ],
)
def test_request_with_invalid_schema_results_in_error_422(api_request, payload):
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url,
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
