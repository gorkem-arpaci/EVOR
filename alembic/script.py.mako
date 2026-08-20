"""Generic Alembic script template used by alembic revision --autogenerate.
This is a trimmed template; it's fine to keep the default Alembic template as-is.
"""

##
## NOTE: This file is used by Alembic; leave it in place for `alembic revision`.
##

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = """${up_revision or ''}"""
down_revision = """${down_revision or None}"""
branch_labels = None
depends_on = None

def upgrade():
    pass


def downgrade():
    pass
