"""empty message

Revision ID: 3187042f56e1
Revises: 
Create Date: 2023-02-16 15:38:13.244995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '3187042f56e1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    connection.execute(text('CREATE SCHEMA IF NOT EXISTS auth;'))

    op.create_table('roles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='auth'
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('login', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('login'),
    schema='auth'
    )
    op.create_table('user_login_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('user_agent', sa.TEXT(), nullable=False),
    sa.Column('auth_date', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('user_device_type', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ),
    sa.PrimaryKeyConstraint('id', 'user_device_type'),
    sa.UniqueConstraint('id', 'user_device_type'),
    schema='auth',
    postgresql_partition_by='LIST (user_device_type)',
    )

    connection = op.get_bind()
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "user_login_history_smart" PARTITION OF "user_login_history" FOR VALUES IN ('smart');
    """))
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "user_login_history_mobile" PARTITION OF "user_login_history" FOR VALUES IN ('mobile')
    """))
    connection.execute(text("""
    CREATE TABLE IF NOT EXISTS "user_login_history_web" PARTITION OF "user_login_history" FOR VALUES IN ('web')
    """))

    op.create_table('user_profile',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('last_name', sa.String(length=256), nullable=False),
    sa.Column('first_name', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('user_id'),
    schema='auth'
    )
    op.create_table('user_refresh_token',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('access_token', sa.TEXT(), nullable=False),
    sa.Column('refresh_token', sa.TEXT(), nullable=False),
    sa.Column('expires', postgresql.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('refresh_token'),
    schema='auth'
    )
    op.create_table('roles_parents',
    sa.Column('role_id', sa.UUID(), nullable=True),
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['auth.roles.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['auth.roles.id'], )
    )
    op.create_table('users_roles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('role_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['auth.roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_roles')
    op.drop_table('roles_parents')
    op.drop_table('user_refresh_token', schema='auth')
    op.drop_table('user_profile', schema='auth')
    op.drop_table('user_login_history', schema='auth')
    op.drop_table('users', schema='auth')
    op.drop_table('roles', schema='auth')
    # ### end Alembic commands ###
