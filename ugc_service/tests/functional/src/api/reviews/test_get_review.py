from http import HTTPStatus
from uuid import uuid4

from testdata import Review
from utils import write_to_db

endpoint_url = '/reviews/{review_id}'
endpoint_method = 'get'


def test_correct_request_returns_a_review_with_code_200(db, api_request):
    review = Review()

    write_to_db(db.reviews, review)

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review.review_id),
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_review = Review.parse_obj(response_body['review'])

    assert response_review.dict(include={'film_id', 'user_id', 'body'}) \
           == review.dict(include={'film_id', 'user_id', 'body'})


def test_request_for_a_nonexistent_review_results_in_error_404(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4()),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_request_for_invalid_review_id_results_in_error_422(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id='invalid'),
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
