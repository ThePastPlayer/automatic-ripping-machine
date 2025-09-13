"""create job_images table

Revision ID: xxxxx_create_job_images
Revises: xxxxx_add_ai_settings
Create Date: 2025-09-13 00:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxxx_create_job_images'
down_revision = 'xxxxx_add_ai_settings'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'job_image',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('side', sa.String(length=16), nullable=False),
        sa.Column('path', sa.String(length=512), nullable=False),
        sa.Column('ocr_text', sa.Text(), nullable=True),
        sa.Column('ocr_lang', sa.String(length=16), nullable=True),
        sa.Column('ocr_conf', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_image_job_id', 'job_image', ['job_id'])


def downgrade():
    op.drop_index('ix_job_image_job_id', table_name='job_image')
    op.drop_table('job_image')


