"""initial

Revision ID: eb0b59a0075a
Revises: 
Create Date: 2024-07-23 04:37:38.110590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb0b59a0075a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('languages',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=31), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('scan_types',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.CHAR(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tags',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=31), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('scans',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('type_id', sa.INTEGER(), server_default=sa.text('(NULL)'), nullable=True),
    sa.Column('format', sa.Enum('TIFF', 'JPEG', 'PNG', name='format'), nullable=True),
    sa.Column('title', sa.VARCHAR(length=255), nullable=False),
    sa.Column('path', sa.VARCHAR(length=1023), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['scan_types.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', 'type_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('documents',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('scan_id', sa.INTEGER(), nullable=False),
    sa.Column('type', sa.Enum('TXT', 'PDF', 'MS_WORD', 'HTML', 'RTF', 'ODT', 'FB2', 'EPUB', 'CSV', name='type'), nullable=True),
    sa.Column('path', sa.VARCHAR(length=1023), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', 'scan_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('scan_tag',
    sa.Column('scan_id', sa.INTEGER(), nullable=False),
    sa.Column('tag_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('scan_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scan_tag')
    op.drop_table('documents')
    op.drop_table('scans')
    op.drop_table('tags')
    op.drop_table('scan_types')
    op.drop_table('languages')
    # ### end Alembic commands ###