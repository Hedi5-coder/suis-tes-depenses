"""creation initiale

Revision ID: 517f22725048
Revises: 
Create Date: 2025-05-12 21:19:09.601398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '517f22725048'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=120), nullable=False),
    sa.Column('budget_mensuel', sa.Float(), nullable=True),
    sa.Column('avatar_style', sa.Integer(), nullable=True),
    sa.Column('devise', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('activite',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('depense',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('montant', sa.Float(), nullable=False),
    sa.Column('categorie', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('depense')
    op.drop_table('activite')
    op.drop_table('user')
    # ### end Alembic commands ###
