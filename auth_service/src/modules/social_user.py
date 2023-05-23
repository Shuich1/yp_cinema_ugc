import uuid
from http import HTTPStatus

from core.init_extension import db
from models.db import SocialAccount, User, UserProfile
from models.http import BaseResponse


def register_social_user(social_name: str, social_id: str,
                         last_name: str, first_name: str, email: str) -> BaseResponse:

    social_acc = SocialAccount.query.filter_by(social_id=social_id, social_name=social_name).one_or_none()
    if social_acc:
        return BaseResponse().load({'msg': 'User already registered'}), HTTPStatus.CONFLICT

    if email == '':
        user_profile = None
    else:
        user_profile = UserProfile.query.filter_by(email=email).one_or_none()

    if user_profile is None:
        user = User(login=f"{social_name}_{social_id}", id=uuid.uuid4())
        db.session.add(user)
        social_acc = SocialAccount(user_id=user.id, social_id=social_id, social_name=social_name)
        db.session.add(social_acc)
        user_profile = UserProfile(
            user_id=user.id,
            last_name=last_name,
            first_name=first_name,
            email=email
        )
        db.session.add(user_profile)
        db.session.commit()
        return BaseResponse().load({'msg': 'User is registered'}), HTTPStatus.OK, social_acc
    else:
        return BaseResponse().load({'msg': 'The email is already used'}), HTTPStatus.CONFLICT
