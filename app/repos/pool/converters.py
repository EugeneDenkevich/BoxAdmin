from app.domain.pool.entities import Pool
from app.infra.db.tables.pool import PoolTable


def pool_db_to_entity(pool: PoolTable) -> Pool:
    return Pool(
        id=pool.id,
        telegram_poll_id=pool.telegram_poll_id,
        created_at=pool.created_at,
        updated_at=pool.updated_at,
    )
