from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from dependencies import get_producer
from models import User, MovieTimecode, MovieTimecodeMessage
from services.auth import JWTBearer
from services.producer import Producer, ProducerError

router = APIRouter(tags=['movies'])


@router.post(
    '/timecode',
    summary='Save movie timecode',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        **JWTBearer.responses,
        HTTPStatus.INTERNAL_SERVER_ERROR.value: {
            'description': 'Service unavailable',
        },
    },
)
async def save_movie_timecode(
        *,
        producer: Producer = Depends(get_producer),
        user: User = Depends(JWTBearer()),
        movie_timecode: MovieTimecode,
):
    message = MovieTimecodeMessage(user_id=user.id, **movie_timecode.dict())
    try:
        await producer.push(
            key=f'{user.id}:{movie_timecode.movie_id}',
            value=message.json(),
        )
    except ProducerError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Service unavailable',
        )
