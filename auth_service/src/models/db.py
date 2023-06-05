from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import List

import flask
from core.config import settings
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from flask_sqlalchemy import SQLAlchemy
from modules.tools import DetectMobileBrowser
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP, UUID
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def create_schema(session):
    session.execute(text('CREATE SCHEMA IF NOT EXISTS auth;'))
    session.commit()


def create_partition_user_login_history(target, connection, **kw) -> None:
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "user_login_history_smart" PARTITION OF "user_login_history" FOR VALUES IN ('smart');
    """))
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "user_login_history_mobile" PARTITION OF "user_login_history" FOR VALUES IN ('mobile')
    """))
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "user_login_history_web" PARTITION OF "user_login_history" FOR VALUES IN ('web')
    """))


def create_partition_social_account(target, connection, **kw) -> None:
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "social_account_vk" PARTITION OF "social_account" FOR VALUES IN ('vk');
    """))
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "social_account_google" PARTITION OF "social_account" FOR VALUES IN ('google');
    """))
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "social_account_yandex" PARTITION OF "social_account" FOR VALUES IN ('yandex');
    """))
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "social_account_mailru" PARTITION OF "social_account" FOR VALUES IN ('mailru');
    """))


def create_user_and_role_if_not_exist(db, login, password, rolename):
    user = User.query.filter_by(login=login).one_or_none()
    if not user:
        role = Role.query.filter_by(name=rolename).one_or_none()
        if not role:
            role = Role(name=rolename)
            db.session.add(role)
        user = User(login=login)
        user.set_password(password=password)
        user.add_role(role)
        db.session.add(user)
        db.session.commit()


users_roles = db.Table(
    'users_roles',
    db.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    db.Column('user_id', UUID, db.ForeignKey('auth.users.id')),
    db.Column('role_id', UUID, db.ForeignKey('auth.roles.id'))
)

roles_parents = db.Table(
    'roles_parents',
    db.Column('role_id', UUID, db.ForeignKey('auth.roles.id')),
    db.Column('parent_id', UUID, db.ForeignKey('auth.roles.id'))
)


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'auth'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    parents = db.relationship(
        'Role',
        secondary=roles_parents,
        primaryjoin=(id == roles_parents.c.role_id),
        secondaryjoin=(id == roles_parents.c.parent_id),
        backref=db.backref('children', lazy='dynamic')
    )

    def add_parent(self, parent):
        self.parents.append(parent)

    def add_parents(self, *parents):
        for parent in parents:
            self.add_parent(parent)

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String)
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('roles', lazy='dynamic')
    )
    refresh_tokens = db.relationship(
        'UserRefreshToken',
        backref=db.backref('users')
    )
    profile = db.relationship(
        'UserProfile',
        backref=db.backref('user_profile')
    )
    history = db.relationship(
        'UserLoginHistory',
        backref=db.backref('user_login_history')
    )

    def set_roles(self, roles: List):
        self.roles = []
        self.add_roles(roles)

    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        for role in roles:
            self.add_role(role)

    def get_roles(self) -> Iterator[Role]:
        for role in self.roles:
            yield role

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def create_app_access_token(self) -> str:
        access_token = create_access_token(
            identity=self, additional_claims={"roles": [role.name for role in self.roles], "login": self.login}
        )
        return access_token

    def create_app_refresh_token(
            self, access_token_jti: str,
            old_refresh_token: UserRefreshToken = None
    ) -> str:
        refresh_token = create_refresh_token(identity=self)
        user_refresh_token = UserRefreshToken(
            user_id=self.id,
            access_token=access_token_jti,
            refresh_token=decode_token(refresh_token)["jti"],
            expires=datetime.now() + timedelta(days=settings.jwt_refresh_token_expires),
        )
        db.session.add(user_refresh_token)
        if old_refresh_token:
            db.session.delete(old_refresh_token)
        db.session.commit()
        return refresh_token

    def check_refresh_token(self, access_token_jti: str, refresh_token_jti: str) -> UserRefreshToken:
        user_refresh_token = UserRefreshToken.query.filter_by(
            user_id=self.id,
            access_token=access_token_jti,
            refresh_token=refresh_token_jti,
        ).one_or_none()
        return user_refresh_token

    def user_login(self) -> dict:
        access_token = self.create_app_access_token()
        refresh_token = self.create_app_refresh_token(access_token_jti=decode_token(access_token)['jti'])
        auth_history = UserLoginHistory(
            user_id=self.id,
            user_agent=flask.request.user_agent.string,
            auth_date=datetime.now(),
            user_device_type=DetectMobileBrowser().process_request()

        )
        db.session.add(auth_history)
        db.session.commit()
        return {
            'id': self.id,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    def __repr__(self):
        return f'<User {self.login}>'


class UserRefreshToken(db.Model):
    __tablename__ = 'user_refresh_token'
    __table_args__ = {'schema': 'auth'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey(User.id))
    access_token = db.Column(TEXT(), unique=True, nullable=False)
    refresh_token = db.Column(TEXT(), unique=True, nullable=False)
    # время жизни храним чтобы можно было легко sql-запросом удалять просроченные токены
    # это более красиво, чем вычитать все токены для расшифровки и удаления просроченных
    expires = db.Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'<User_id {self.user_id}\n Refresh token {self.refresh_token}>'


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    __table_args__ = {'schema': 'auth'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey(User.id), unique=True, nullable=False)
    last_name = db.Column(db.String(256), unique=False, nullable=False)
    first_name = db.Column(db.String(256), unique=False, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)

    def __repr__(self):
        return f'<User_id {self.user_id} first name {self.first_name} last name {self.last_name}>'


class UserLoginHistory(db.Model):
    __tablename__ = 'user_login_history'
    __table_args__ = (
                         db.UniqueConstraint('id', 'user_device_type'),
                         {
                             'schema': 'auth',
                             'postgresql_partition_by': 'LIST (user_device_type)',
                             'listeners': [('after_create', create_partition_user_login_history)],
                         }

    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey(User.id), nullable=False)
    user_agent = db.Column(TEXT(), nullable=False)
    auth_date = db.Column(TIMESTAMP, nullable=False)
    user_device_type = db.Column(TEXT(), primary_key=True)

    def __repr__(self):
        return f'<User_id {self.user_id} user agent {self.user_agent} auth date {self.auth_date}>'


class SocialAccount(db.Model):
    __tablename__ = 'social_account'
    __table_args__ = (
                         db.UniqueConstraint('social_id', 'social_name', name='social_pk'),
                         db.UniqueConstraint('id', 'social_name', name='id_pk'),
                         {
                             'schema': 'auth',
                             'postgresql_partition_by': 'LIST (social_name)',
                             'listeners': [('after_create', create_partition_social_account)],
                         }
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False, primary_key=True)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
