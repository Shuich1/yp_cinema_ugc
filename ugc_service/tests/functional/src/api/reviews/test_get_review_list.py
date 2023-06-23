from http import HTTPStatus
from random import randint
from uuid import uuid4

import pytest

from testdata import Review
from utils import write_to_db

endpoint_url = '/reviews/'
endpoint_method = 'get'


def test_correct_request_returns_a_list_of_reviews_with_code_200(
        db,
        api_request,
):
    reviews = [Review() for _ in range(10)]
    review_ids = {review.review_id for review in reviews}

    write_to_db(db.reviews, *reviews)

    response = api_request(endpoint_method, endpoint_url)

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_reviews = [
        Review.parse_obj(obj)
        for obj in response_body['reviews']
    ]
    response_review_ids = {review.review_id for review in response_reviews}

    assert response_review_ids == review_ids


@pytest.mark.parametrize(
    ['db_count', 'offset', 'limit', 'response_count'],
    [
        (10, None, 5, 5),
        (10, 2, None, 8),
        (10, 2, 5, 5),
        (10, 12, None, 0),
        (10, None, 12, 10),
    ],
)
def test_request_with_pagination_params_returns_correct_page_with_code_200(
        db,
        api_request,
        db_count,
        offset,
        limit,
        response_count,
):
    reviews = [Review() for _ in range(10)]
    review_ids = {review.review_id for review in reviews}

    write_to_db(db.reviews, *reviews)

    params = {}
    offset and params.update({'offset': offset})
    limit and params.update({'limit': limit})

    response = api_request(endpoint_method, endpoint_url, params=params)

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_reviews = [
        Review.parse_obj(obj)
        for obj in response_body['reviews']
    ]
    response_review_ids = {review.review_id for review in response_reviews}

    assert response_review_ids <= review_ids
    assert len(response_review_ids) == response_count


@pytest.mark.parametrize(
    ['filter_params', 'relevant_count'],
    [
        ({'film_id': uuid4()}, 5),
        ({'user_id': uuid4()}, 5),
        ({'film_id': uuid4(), 'user_id': uuid4()}, 1),
    ]
)
def test_request_with_filtering_params_returns_correct_result_with_code_200(
        db,
        api_request,
        filter_params,
        relevant_count,
):
    relevant_reviews = [Review(**filter_params) for _ in range(relevant_count)]
    relevant_review_ids = {review.review_id for review in relevant_reviews}

    reviews = relevant_reviews + [Review() for _ in range(10)]

    write_to_db(db.reviews, *reviews)

    response = api_request(endpoint_method, endpoint_url, params=filter_params)

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_reviews = [
        Review.parse_obj(obj)
        for obj in response_body['reviews']
    ]
    response_review_ids = {review.review_id for review in response_reviews}

    assert response_review_ids == relevant_review_ids
    assert len(response_review_ids) == relevant_count


@pytest.mark.parametrize(
    ['sorting_key', 'reverse', 'sorting_query_param'],
    [
        (lambda review: review.created, False, 'created:asc',),
        (lambda review: review.created, True, 'created:desc',),
        (lambda review: review.likes - review.dislikes, False, 'rating:asc',),
        (lambda review: review.likes - review.dislikes, True, 'rating:desc',),
        (lambda review: review.likes + review.dislikes, False, 'votes:asc',),
        (lambda review: review.likes + review.dislikes, True, 'votes:desc',),
    ]
)
def test_request_with_sorting_params_returns_correct_result_with_code_200(
        db,
        api_request,
        sorting_key,
        reverse,
        sorting_query_param,
):
    reviews = [
        Review(likes=randint(0, 10), dislikes=randint(0, 10))
        for _ in range(10)
    ]
    sorted_reviews = sorted(reviews, key=sorting_key, reverse=reverse)
    sorted_review_keys = [sorting_key(review) for review in sorted_reviews]

    write_to_db(db.reviews, *reviews)

    response = api_request(
        endpoint_method,
        endpoint_url,
        params={'sort': sorting_query_param},
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_reviews = [
        Review.parse_obj(obj)
        for obj in response_body['reviews']
    ]
    response_review_keys = [sorting_key(review) for review in response_reviews]

    assert response_review_keys == sorted_review_keys


@pytest.mark.parametrize(
    ['params'],
    [
        ({'film_id': 'invalid'},),
        ({'user_id': 'invalid'},),
        ({'offset': -5},),
        ({'offset': 'invalid'},),
        ({'limit': -5},),
        ({'limit': 300},),
        ({'limit': 'invalid'},),
        ({'sort': 'created'},),
        ({'sort': 'id:desc'},),
    ]
)
def test_request_with_invalid_params_results_in_error_422(api_request, params):
    response = api_request(endpoint_method, endpoint_url, params=params)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
