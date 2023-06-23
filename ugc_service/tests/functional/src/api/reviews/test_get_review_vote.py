from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Review, ReviewVote
from utils import write_to_db

endpoint_url = '/reviews/{review_id}/votes/{user_id}'
endpoint_method = 'get'


def test_correct_request_returns_a_vote_with_code_200(db, api_request):
    review = Review()
    write_to_db(db.reviews, review)

    review_vote = ReviewVote(review_id=review.review_id)
    write_to_db(db.review_votes, review_vote)

    response = api_request(
        endpoint_method,
        endpoint_url.format(
            review_id=review_vote.review_id,
            user_id=review_vote.user_id,
        ),
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_review_vote = ReviewVote.parse_obj(response_body['review_vote'])

    assert response_review_vote.id == review_vote.id


def test_request_for_a_nonexistent_rating_results_in_error_404(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4(), user_id=uuid4()),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ['review_id', 'user_id'],
    [(uuid4(), 'invalid'), ('invalid', uuid4())],
)
def test_request_for_invalid_rating_id_results_in_error_422(
        api_request,
        review_id,
        user_id,
):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_id, user_id=user_id),
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
