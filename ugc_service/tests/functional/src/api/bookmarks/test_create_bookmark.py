from http import HTTPStatus
from uuid import uuid4

from testdata import Bookmark
from utils import write_to_db, extract_from_db

endpoint_url = '/bookmarks/'
endpoint_method = 'post'


def test_correct_authenticated_request_creates_and_returns_a_bookmark_with_code_201(
        db,
        api_request,
):
    user_id = uuid4()
    bookmark = Bookmark(user_id=user_id)

    payload = {'film_id': str(bookmark.film_id)}
    response = api_request(
        endpoint_method,
        endpoint_url,
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.CREATED

    response_body = response.json()
    response_bookmark = Bookmark.parse_obj(response_body['bookmark'])

    search_params = bookmark.dict(exclude={'created'})
    db_bookmark = extract_from_db(Bookmark, db.bookmarks, search_params)

    assert response_bookmark.id == db_bookmark.id


def test_unauthenticated_request_results_in_error_401(api_request):
    bookmark = Bookmark()

    payload = {'film_id': str(bookmark.film_id)}
    response = api_request(endpoint_method, endpoint_url, json=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_attempt_to_create_already_existing_bookmark_results_in_error_409(
        db,
        api_request,
):
    user_id = uuid4()
    bookmark = Bookmark(user_id=user_id)

    write_to_db(db.bookmarks, bookmark)

    payload = {'film_id': str(bookmark.film_id)}
    response = api_request(
        endpoint_method,
        endpoint_url,
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_request_with_invalid_film_id_results_in_error_422(api_request):
    film_id = 'invalid'
    user_id = uuid4()

    payload = {'film_id': film_id}
    response = api_request(
        endpoint_method,
        endpoint_url,
        user_id=user_id,
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
