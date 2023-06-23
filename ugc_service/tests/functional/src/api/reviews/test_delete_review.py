from http import HTTPStatus
from uuid import uuid4

from testdata import Review
from utils import write_to_db, extract_from_db

endpoint_url = '/reviews/{review_id}'
endpoint_method = 'delete'


def test_correct_authenticated_request_deletes_a_review_with_code_204(
        db,
        api_request,
):
    user_id = uuid4()
    review = Review(user_id=user_id)

    write_to_db(db.reviews, review)

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review.review_id),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    search_params = {'review_id': review.review_id}
    db_review = extract_from_db(Review, db.reviews, search_params)

    assert db_review is None


def test_unauthenticated_request_results_in_error_401(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4()),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_unauthorized_request_results_in_error_403(
        db,
        api_request,
):
    user_id = uuid4()
    review = Review(user_id=user_id)

    write_to_db(db.reviews, review)

    other_user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review.review_id),
        user_id=other_user_id,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_for_a_nonexistent_review_results_in_error_404(api_request):
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4()),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_request_for_invalid_review_id_results_in_error_422(api_request):
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id='invalid'),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
