from app.domain.user.entities import User
from app.infra.db.tables.user import UserTable


def user_db_to_entity(user: UserTable) -> User:
    return User(
        id=user.id,
        tg_id=user.tg_id,
        username=user.username,
        is_admin=user.is_admin,
        is_staff=user.is_staff,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
