from marshmallow import EXCLUDE, Schema, fields


class BaseResponse(Schema):
    msg = fields.Str(required=True)


class IDScheme(Schema):
    id = fields.UUID(required=True)


class LoginScheme(Schema):
    login = fields.Str(required=True)


class UserScheme(IDScheme, LoginScheme):
    pass


class LoginPasswordScheme(LoginScheme):
    password = fields.Str(required=True)


class AccessTokenScheme(Schema):
    access_token = fields.Str(required=True)


class RefreshTokenScheme(Schema):
    refresh_token = fields.Str(required=True)


class AccessRefreshTokenScheme(AccessTokenScheme, RefreshTokenScheme):
    pass


class RoleSchema(Schema):
    id = fields.UUID()
    name = fields.Str(required=True)


class RoleIdNameSchema(RoleSchema):
    id = fields.UUID(required=True)


class ProfileSchema(Schema):
    email = fields.Email(required=True)
    last_name = fields.Str(required=True)
    first_name = fields.Str(required=True)


class LoginHistorySchema(Schema):
    id = fields.UUID(required=True)
    user_agent = fields.Str(required=True)
    date = fields.DateTime(required=True, format='iso')


class UserRolesScheme(UserScheme):
    roles = fields.List(fields.Str())


class UserCreateScheme(Schema):
    login = fields.Str(required=True)
    password = fields.Str(required=True)
    id = fields.UUID()
    roles = fields.List(fields.Str())


class VKOAUTH2Scheme(Schema):
    access_token = fields.Str(required=True)
    user_id = fields.Int(required=True)
    email = fields.Email(required=True)
    expires_in = fields.Int(required=True)


class BaseOAuthTokensSchema(Schema):
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    expires_in = fields.Int(required=True)
    token_type = fields.Str(required=True)


class YandexUserSchema(Schema):
    id = fields.Str(required=True)
    login = fields.Str(required=True)
    default_email = fields.Str(required=True)
    client_id = fields.Str(required=True)
    psuid = fields.Str(required=True)
    display_name = fields.Str(allow_none=True)
    real_name = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    sex = fields.Str(allow_none=True)

    class Meta:
        unknown = EXCLUDE


class MailruUserSchema(Schema):
    id = fields.Str(required=True)
    nickname = fields.Str(allow_none=True)
    email = fields.Str(required=True)
    client_id = fields.Str(required=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    gender = fields.Str(allow_none=True)
    birthday = fields.Str(allow_none=True)

    class Meta:
        unknown = EXCLUDE
