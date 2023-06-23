from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Review, ReviewVote
from utils import write_to_db, extract_from_db

endpoint_url = '/reviews/{review_id}/votes/{user_id}'
endpoint_method = 'delete'


def test_correct_authenticated_request_deletes_a_vote_with_code_204(
        db,
        api_request,
):
    review = Review()
    write_to_db(db.reviews, review)

    user_id = uuid4()
    review_vote = ReviewVote(review_id=review.review_id, user_id=user_id)
    write_to_db(db.review_votes, review_vote)

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_vote.review_id, user_id=user_id),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_unauthenticated_request_results_in_error_401(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4(), user_id=uuid4()),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_unauthorized_request_results_in_error_403(
        db,
        api_request,
):
    review = Review()
    write_to_db(db.reviews, review)

    user_id = uuid4()
    review_vote = ReviewVote(review_id=review.review_id, user_id=user_id)
    write_to_db(db.review_votes, review_vote)

    other_user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_vote.review_id, user_id=user_id),
        user_id=other_user_id,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_for_a_nonexistent_vote_results_in_error_404(api_request):
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4(), user_id=user_id),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ['review_id', 'user_id'],
    [(uuid4(), 'invalid'), ('invalid', uuid4())],
)
def test_request_for_invalid_vote_id_results_in_error_422(
        api_request,
        review_id,
        user_id,
):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_id, user_id=user_id),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
