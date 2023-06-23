from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Rating
from utils import write_to_db, extract_from_db

endpoint_url = '/ratings/{film_id}/{user_id}'
endpoint_method = 'put'


def test_correct_authenticated_request_updates_a_rating_with_code_200(
        db,
        api_request,
):
    user_id = uuid4()
    rating = Rating(user_id=user_id, rating=10)

    write_to_db(db.ratings, rating)

    rating.rating = 9

    payload = {'rating': rating.rating}
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=rating.film_id, user_id=user_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_rating = Rating.parse_obj(response_body['rating'])

    search_params = rating.dict(exclude={'created', 'updated'})
    db_rating = extract_from_db(Rating, db.ratings, search_params)

    assert response_rating.id == db_rating.id
    assert response_rating.rating == db_rating.rating


def test_unauthenticated_request_results_in_error_401(api_request):
    payload = {'rating': 5}
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=uuid4()),
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_unauthorized_request_results_in_error_403(
        db,
        api_request,
):
    user_id = uuid4()
    rating = Rating(user_id=user_id, rating=7)

    write_to_db(db.ratings, rating)

    rating.rating = 8

    other_user_id = uuid4()

    payload = {'rating': rating.rating}
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=rating.film_id, user_id=user_id),
        user_id=other_user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_for_a_nonexistent_rating_results_in_error_404(api_request):
    user_id = uuid4()

    payload = {'rating': 8}
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=user_id),
        user_id=user_id,
        json=payload,
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
    payload = {'rating': 4}
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=film_id, user_id=user_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    ['payload'],
    [
        ({'rating': 'invalid'},),
        ({'rating': 11},),
        ({'rating': -2},),
        ({'invalid': 'invalid'},),
    ],
)
def test_request_with_invalid_schema_results_in_error_422(api_request, payload):
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=user_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
