from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Review
from utils import extract_from_db

endpoint_url = '/reviews/'
endpoint_method = 'post'


def test_correct_authenticated_request_creates_and_returns_a_review_with_code_201(
        db,
        api_request,
):
    user_id = uuid4()
    review = Review(user_id=user_id)

    payload = {'film_id': str(review.film_id), 'body': review.body}
    response = api_request(
        endpoint_method,
        endpoint_url,
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.CREATED

    response_body = response.json()
    response_review = Review.parse_obj(response_body['review'])

    search_params = {'review_id': response_review.review_id}
    db_review = extract_from_db(Review, db.reviews, search_params)

    assert response_review.review_id == db_review.review_id


def test_unauthenticated_request_results_in_error_401(api_request):
    review = Review()

    payload = {'film_id': str(review.film_id), 'body': review.body}
    response = api_request(
        endpoint_method,
        endpoint_url,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    ['payload'],
    [
        ({'film_id': 'invalid', 'body': 'test'},),
        ({'film_id': str(uuid4()), 'body': 'x' * 2023},),
        ({'film_id': str(uuid4())},),
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
