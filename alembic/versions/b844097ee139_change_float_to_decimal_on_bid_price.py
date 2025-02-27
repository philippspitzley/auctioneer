"""change float to decimal on bid price

Revision ID: b844097ee139
Revises: ae6ab3624587
Create Date: 2025-02-24 11:03:25.573892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'b844097ee139'
down_revision: Union[str, None] = 'ae6ab3624587'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bid', 'amount',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.Numeric(scale=2),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bid', 'amount',
               existing_type=sa.Numeric(scale=2),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=False)
    # ### end Alembic commands ###
