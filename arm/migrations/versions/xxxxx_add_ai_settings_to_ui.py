"""add ai settings to ui_settings

Revision ID: xxxxx_add_ai_settings
Revises: 9cae4aa05dd7
Create Date: 2025-09-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxxx_add_ai_settings'
down_revision = '9cae4aa05dd7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ui_settings') as batch_op:
        batch_op.add_column(sa.Column('notify_refresh', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('openai_api_key', sa.String(length=256), nullable=True))
        batch_op.add_column(sa.Column('tmdb_api_key', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('omdb_api_key', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('musicbrainz_useragent', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('musicbrainz_contact', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('discogs_token', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('enable_ai_identification', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('enable_cd_track_renaming', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('min_clip_duration_seconds', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('ui_settings') as batch_op:
        batch_op.drop_column('min_clip_duration_seconds')
        batch_op.drop_column('enable_cd_track_renaming')
        batch_op.drop_column('enable_ai_identification')
        batch_op.drop_column('discogs_token')
        batch_op.drop_column('musicbrainz_contact')
        batch_op.drop_column('musicbrainz_useragent')
        batch_op.drop_column('omdb_api_key')
        batch_op.drop_column('tmdb_api_key')
        batch_op.drop_column('openai_api_key')
        batch_op.drop_column('notify_refresh')


