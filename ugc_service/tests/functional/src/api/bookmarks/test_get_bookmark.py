from http import HTTPStatus
from uuid import uuid4

import pytest

from testdata import Bookmark
from utils import write_to_db

endpoint_url = '/bookmarks/{film_id}/{user_id}'
endpoint_method = 'get'


def test_correct_request_returns_a_bookmarks_with_code_200(db, api_request):
    bookmark = Bookmark()

    write_to_db(db.bookmarks, bookmark)

    response = api_request(
        endpoint_method,
        endpoint_url.format(
            film_id=bookmark.film_id,
            user_id=bookmark.user_id,
        ),
    )

    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    response_bookmark = Bookmark.parse_obj(payload['bookmark'])

    assert response_bookmark.id == bookmark.id


def test_request_for_a_nonexistent_bookmark_results_in_error_404(api_request):
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=uuid4()),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ['film_id', 'user_id'],
    [(uuid4(), 'invalid'), ('invalid', uuid4())],
)
def test_request_for_invalid_bookmark_id_results_in_error_422(
        api_request,
        film_id,
        user_id,
):
    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=film_id, user_id=user_id),
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
