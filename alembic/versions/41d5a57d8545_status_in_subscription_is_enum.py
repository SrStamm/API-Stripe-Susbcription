"""status in Subscription is Enum

Revision ID: 41d5a57d8545
Revises: 005bf460cdbe
Create Date: 2026-04-20 15:26:14.627110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41d5a57d8545'
down_revision: Union[str, Sequence[str], None] = '005bf460cdbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Normalización: Mapeamos los estados "legacy" a los estados de tu Enum oficial
    # 'free' -> 'incomplete' (o el que consideres mejor punto de partida)
    # 'active' -> 'paid' (asumiendo que 'active' es suscripción pagada)
    # 'open' -> 'incomplete'
    # 'canceled' -> 'unpaid' (o 'incomplete')
    op.execute("UPDATE subscriptions SET status = 'incomplete' WHERE status = 'free'")
    op.execute("UPDATE subscriptions SET status = 'paid' WHERE status = 'active'")
    op.execute("UPDATE subscriptions SET status = 'incomplete' WHERE status = 'open'")
    op.execute("UPDATE subscriptions SET status = 'unpaid' WHERE status = 'canceled'")

    # 2. Crear el tipo de forma segura (usando la lista de enums.py)
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subscriptionstatus') THEN
                CREATE TYPE subscriptionstatus AS ENUM (
                    'incomplete', 'trialing', 'past_due', 'unpaid', 'paid'
                );
            END IF;
        END $$;
    """)

    # 3. Conversión de tipo
    op.execute("ALTER TABLE subscriptions ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE subscriptions ALTER COLUMN status TYPE subscriptionstatus USING status::text::subscriptionstatus")

    # 4. Restaurar el default
    op.execute("ALTER TABLE subscriptions ALTER COLUMN status SET DEFAULT 'incomplete'::subscriptionstatus")

def downgrade() -> None:
    # Para revertir, primero debemos quitar los defaults y convertir a VARCHAR
    op.execute("ALTER TABLE subscriptions ALTER COLUMN tier DROP DEFAULT")
    op.execute("ALTER TABLE subscriptions ALTER COLUMN status DROP DEFAULT")
    
    op.execute("ALTER TABLE subscriptions ALTER COLUMN tier TYPE VARCHAR USING tier::text")
    op.execute("ALTER TABLE subscriptions ALTER COLUMN status TYPE VARCHAR USING status::text")
    
    # Finalmente, borrar los tipos
    op.execute("DROP TYPE subscriptiontier")
    op.execute("DROP TYPE subscriptionstatus")
