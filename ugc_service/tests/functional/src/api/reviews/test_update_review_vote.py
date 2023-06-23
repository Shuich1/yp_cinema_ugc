from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Review, ReviewVote
from utils import write_to_db, extract_from_db

endpoint_url = '/reviews/{review_id}/votes/{user_id}'
endpoint_method = 'put'


@pytest.mark.parametrize(
    ['initial_vote', 'new_vote', 'likes_incr', 'dislikes_incr'],
    [
        ('like', 'dislike', -1, 1),
        ('dislike', 'like', 1, -1),
    ],
)
def test_correct_authenticated_request_updates_a_vote_with_code_200(
        db,
        api_request,
        initial_vote,
        new_vote,
        likes_incr,
        dislikes_incr,
):
    review = Review()
    write_to_db(db.reviews, review)

    user_id = uuid4()
    review_vote = ReviewVote(
        review_id=review.review_id,
        user_id=user_id,
        vote=initial_vote,
    )
    write_to_db(db.review_votes, review_vote)

    payload = {'vote': new_vote}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_vote.review_id, user_id=user_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.OK

    search_params = review_vote.dict(exclude={'vote'})
    db_vote = extract_from_db(ReviewVote, db.review_votes, search_params)

    assert db_vote.vote == new_vote

    search_params = {'review_id': review.review_id}
    db_review = extract_from_db(Review, db.reviews, search_params)

    assert db_review.likes - review.likes == likes_incr
    assert db_review.dislikes - review.dislikes == dislikes_incr


def test_unauthenticated_request_results_in_error_401(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4(), user_id=uuid4()),
        json={'vote': 'like'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_unauthorized_request_results_in_error_403(db, api_request):
    review = Review()
    write_to_db(db.reviews, review)

    user_id = uuid4()
    review_vote = ReviewVote(review_id=review.review_id, user_id=user_id)
    write_to_db(db.review_votes, review_vote)

    other_user_id = uuid4()

    payload = {'vote': 'like'}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_vote.review_id, user_id=user_id),
        user_id=other_user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_for_a_nonexistent_vote_results_in_error_404(api_request):
    user_id = uuid4()

    payload = {'vote': 'like'}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4(), user_id=user_id),
        user_id=user_id,
        json=payload,
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
    payload = {'vote': 'like'}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=review_id, user_id=user_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_request_with_invalid_schema_results_in_error_422(api_request):
    user_id = uuid4()

    payload = {'vote': 'invalid'}
    response = api_request(
        endpoint_method,
        endpoint_url.format(review_id=uuid4(), user_id=user_id),
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
