from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Bookmark
from utils import write_to_db

endpoint_url = '/bookmarks/'
endpoint_method = 'get'


def test_correct_request_returns_a_list_of_bookmarks_with_code_200(
        db,
        api_request,
):
    user_id = uuid4()

    bookmarks = [Bookmark(user_id=user_id) for _ in range(10)]
    bookmark_ids = {bookmark.id for bookmark in bookmarks}

    write_to_db(db.bookmarks, *bookmarks)

    response = api_request(
        endpoint_method,
        endpoint_url,
        params={'user_id': user_id},
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_bookmarks = [
        Bookmark.parse_obj(obj)
        for obj in response_body['bookmarks']
    ]
    response_bookmark_ids = {bookmark.id for bookmark in response_bookmarks}

    assert response_bookmark_ids == bookmark_ids


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
    user_id = uuid4()

    bookmarks = [Bookmark(user_id=user_id) for _ in range(db_count)]
    bookmark_ids = {bookmark.id for bookmark in bookmarks}

    write_to_db(db.bookmarks, *bookmarks)

    params = {'user_id': user_id}
    offset and params.update({'offset': offset})
    limit and params.update({'limit': limit})

    response = api_request(endpoint_method, endpoint_url, params=params)

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    response_bookmarks = [
        Bookmark.parse_obj(obj)
        for obj in response_body['bookmarks']
    ]
    response_bookmark_ids = {bookmark.id for bookmark in response_bookmarks}

    assert response_bookmark_ids <= bookmark_ids
    assert len(response_bookmark_ids) == response_count


def test_request_for_nonexistent_user_id_returns_an_empty_list_with_code_200(
        db,
        api_request,
):
    user_id = uuid4()

    bookmarks = [Bookmark(user_id=user_id) for _ in range(10)]

    write_to_db(db.bookmarks, *bookmarks)

    other_user_id = uuid4()
    response = api_request(
        endpoint_method,
        endpoint_url,
        params={'user_id': other_user_id},
    )

    assert response.status_code == HTTPStatus.OK

    response_body = response.json()

    assert response_body['bookmarks'] == []


def test_request_for_invalid_user_id_results_in_error_422(api_request):
    user_id = 'invalid'

    response = api_request(
        endpoint_method,
        endpoint_url,
        params={'user_id': user_id},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    ['pagination_params'],
    [
        ({'offset': -5},),
        ({'offset': 'invalid'},),
        ({'limit': -5},),
        ({'limit': 300},),
        ({'limit': 'invalid'},),
    ]
)
def test_request_with_invalid_pagination_params_results_in_error_422(
        api_request,
        pagination_params,
):
    params = {'user_id': uuid4()}
    params.update(**pagination_params)
    response = api_request(endpoint_method, endpoint_url, params=params)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
