from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Review, ReviewVote
from utils import write_to_db, extract_from_db

endpoint_url = '/reviews/{review_id}/votes/'
endpoint_method = 'post'


@pytest.mark.parametrize(
    ['vote', 'incr_field'],
    [('like', 'likes'), ('dislike', 'dislikes')],
)
def test_correct_authenticated_request_creates_and_returns_a_vote_with_code_201(
        db,
        api_request,
        vote,
        incr_field,
):
    review = Review()
    write_to_db(db.reviews, review)

    user_id = uuid4()
    review_vote = ReviewVote(
        review_id=review.review_id,
        user_id=user_id,
        vote=vote,
    )

    payload = {'vote': review_vote.vote}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_vote.review_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.CREATED

    response_body = response.json()
    response_vote = ReviewVote.parse_obj(response_body['review_vote'])

    search_params = review_vote.dict(exclude={'vote'})
    db_vote = extract_from_db(ReviewVote, db.review_votes, search_params)

    assert response_vote.id == db_vote.id

    search_params = {'review_id': review.review_id}
    db_review = extract_from_db(Review, db.reviews, search_params)

    assert getattr(db_review, incr_field) - getattr(review, incr_field) == 1


def test_unauthenticated_request_results_in_error_401(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4()),
        json={'vote': 'like'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_attempt_to_create_already_existing_vote_results_in_error_409(
        db,
        api_request,
):
    review = Review()
    write_to_db(db.reviews, review)

    user_id = uuid4()
    review_vote = ReviewVote(
        review_id=review.review_id,
        user_id=user_id,
        vote='like',
    )

    write_to_db(db.review_votes, review_vote)

    payload = {'vote': review_vote.vote}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_vote.review_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_request_with_invalid_schema_results_in_error_422(api_request):
    user_id = uuid4()

    payload = {'vote': 'invalid'}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4()),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
