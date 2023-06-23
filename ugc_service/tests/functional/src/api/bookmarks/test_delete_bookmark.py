from http import HTTPStatus
from uuid import uuid4

from testdata import Bookmark
from utils import write_to_db, extract_from_db

endpoint_url = '/bookmarks/{film_id}/{user_id}'
endpoint_method = 'delete'


def test_correct_authenticated_request_deletes_a_bookmark_with_code_204(
        db,
        api_request,
):
    user_id = uuid4()
    bookmark = Bookmark(user_id=user_id)

    write_to_db(db.bookmarks, bookmark)

    response = api_request(
        endpoint_method,
        endpoint_url.format(
            film_id=bookmark.film_id,
            user_id=bookmark.user_id,
        ),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    search_params = bookmark.dict(exclude={'created'})
    db_bookmark = extract_from_db(Bookmark, db.bookmarks, search_params)

    assert db_bookmark is None


def test_unauthenticated_request_results_in_error_401(db, api_request):
    user_id = uuid4()
    bookmark = Bookmark(user_id=user_id)

    write_to_db(db.bookmarks, bookmark)

    response = api_request(
        endpoint_method,
        endpoint_url.format(
            film_id=bookmark.film_id,
            user_id=bookmark.user_id,
        ),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_unauthorized_request_results_in_error_403(db, api_request):
    user_id = uuid4()
    bookmark = Bookmark(user_id=user_id)

    write_to_db(db.bookmarks, bookmark)

    other_user_id = uuid4()
    response = api_request(
        endpoint_method,
        endpoint_url.format(
            film_id=bookmark.film_id,
            user_id=bookmark.user_id,
        ),
        user_id=other_user_id,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_request_for_a_nonexistent_bookmark_results_in_error_404(api_request):
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=uuid4(), user_id=user_id),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_request_for_invalid_bookmark_id_results_in_error_422(api_request):
    film_id = 'invalid'
    user_id = uuid4()

    response = api_request(
        endpoint_method,
        endpoint_url.format(film_id=film_id, user_id=user_id),
        user_id=user_id,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
