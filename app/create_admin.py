from sqlmodel import Session

from .config import ADMIN_PASSWORD, ADMIN_USERNAME
from .db_handler import engine
from .models.user_model import Role, User, UserCreate
from .utils.auth import get_password_hash


def create_admin_user():
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return

    with Session(engine) as session:
        user = UserCreate(
            username=ADMIN_USERNAME,
            email="admin@mail.com",
            password=ADMIN_PASSWORD,
            role=Role.admin,
        )
        hashed_password = get_password_hash(user.password)
        del user.password
        db_user = User(**user.model_dump(), password_hash=hashed_password)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
