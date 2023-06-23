from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Rating
from utils import write_to_db

endpoint_url = '/ratings/'
endpoint_method = 'get'


def test_correct_request_returns_a_list_of_ratings_with_code_200(
        db,
        api_request,
):
    ratings = [Rating() for _ in range(10)]
    rating_ids = {rating.id for rating in ratings}

    write_to_db(db.ratings, *ratings)

    response = api_request(endpoint_method, endpoint_url)

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_ratings = [
        Rating.parse_obj(obj)
        for obj in response_body['ratings']
    ]
    response_rating_ids = {rating.id for rating in response_ratings}

    assert response_rating_ids == rating_ids


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
    ratings = [Rating() for _ in range(db_count)]
    rating_ids = {rating.id for rating in ratings}

    write_to_db(db.ratings, *ratings)

    params = {}
    offset and params.update({'offset': offset})
    limit and params.update({'limit': limit})

    response = api_request(endpoint_method, endpoint_url, params=params)

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_ratings = [
        Rating.parse_obj(obj)
        for obj in response_body['ratings']
    ]
    response_rating_ids = {rating.id for rating in response_ratings}

    assert response_rating_ids <= rating_ids
    assert len(response_rating_ids) == response_count


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
    relevant_ratings = [Rating(**filter_params) for _ in range(relevant_count)]
    relevant_rating_ids = {rating.id for rating in relevant_ratings}

    ratings = relevant_ratings + [Rating() for _ in range(10)]

    write_to_db(db.ratings, *ratings)

    response = api_request(endpoint_method, endpoint_url, params=filter_params)

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_ratings = [
        Rating.parse_obj(obj)
        for obj in response_body['ratings']
    ]
    response_rating_ids = {rating.id for rating in response_ratings}

    assert response_rating_ids == relevant_rating_ids
    assert len(response_rating_ids) == relevant_count


@pytest.mark.parametrize(
    ['params'],
    [
        ({'offset': -5},),
        ({'offset': 'invalid'},),
        ({'limit': -5},),
        ({'limit': 300},),
        ({'limit': 'invalid'},),
        ({'film_id': 'invalid'},),
        ({'user_id': 'invalid'},),
    ]
)
def test_request_with_invalid_params_results_in_error_422(api_request, params):
    response = api_request(endpoint_method, endpoint_url, params=params)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
