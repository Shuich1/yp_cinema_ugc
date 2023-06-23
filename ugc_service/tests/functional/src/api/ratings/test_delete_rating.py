from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Rating
from utils import write_to_db, extract_from_db

endpoint_url = '/ratings/{film_id}/{user_id}'
endpoint_method = 'delete'


def test_correct_authenticated_request_deletes_a_rating_with_code_204(
        db,
        api_request,
):
    user_id = uuid4()
    rating = Rating(user_id=user_id)

    write_to_db(db.ratings, rating)

    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=rating.film_id, user_id=user_id),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    search_params = rating.dict(exclude={'created', 'updated'})
    db_rating = extract_from_db(Rating, db.ratings, search_params)

    assert db_rating is None


def test_unauthenticated_request_results_in_error_401(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=uuid4()),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_unauthorized_request_results_in_error_403(
        db,
        api_request,
):
    user_id = uuid4()
    rating = Rating(user_id=user_id)

    write_to_db(db.ratings, rating)

    other_user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=rating.film_id, user_id=user_id),
        user_id=other_user_id,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_for_a_nonexistent_rating_results_in_error_404(api_request):
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=user_id),
        user_id=user_id,
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
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
