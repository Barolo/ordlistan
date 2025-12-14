"""fix fk to users table

Revision ID: 336e2b388cd3
Revises: 98512b70ce94
Create Date: 2025-12-10 13:36:32.640894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '336e2b388cd3'
down_revision = '98512b70ce94'
branch_labels = None
depends_on = None


def upgrade():
    # Rename table user -> users
    op.rename_table('user', 'users')

    # Fix foreign keys on dependent tables
    op.drop_constraint('word_list_user_id_fkey', 'word_list', type_='foreignkey')
    op.create_foreign_key(
        None, 'word_list', 'users',
        ['user_id'], ['id']
    )

    op.drop_constraint('quiz_result_user_id_fkey', 'quiz_result', type_='foreignkey')
    op.create_foreign_key(
        None, 'quiz_result', 'users',
        ['user_id'], ['id']
    )

    # Create quiz_answer_log
    op.create_table(
        'quiz_answer_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('quiz_result_id', sa.Integer(), sa.ForeignKey('quiz_result.id'), nullable=False),
        sa.Column('word_id', sa.Integer(), sa.ForeignKey('word.id'), nullable=False),
        sa.Column('user_answer', sa.String(length=255), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('quiz_answer_log')

    op.drop_constraint(None, 'quiz_result', type_='foreignkey')
    op.create_foreign_key(
        'quiz_result_user_id_fkey', 'quiz_result', 'user',
        ['user_id'], ['id']
    )

    op.drop_constraint(None, 'word_list', type_='foreignkey')
    op.create_foreign_key(
        'word_list_user_id_fkey', 'word_list', 'user',
        ['user_id'], ['id']
    )

    op.rename_table('users', 'user')
