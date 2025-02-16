from datetime import datetime, timezone

import bcrypt
from colorama import Back, Fore, Style
from sqlmodel import Session, create_engine

from .config import DB_URI


def get_current_timestamp():
    return datetime.now(timezone.utc)


def get_password_hash(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password, hashed_password):
    hashed_password_enc = hashed_password.encode("utf-8")
    password_byte_enc = plain_password.encode("utf-8")
    return bcrypt.checkpw(
        password=password_byte_enc, hashed_password=hashed_password_enc
    )


# database connection
engine = create_engine(DB_URI, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


def pretty_print(topic: str, message: str):
    msg = (
        f"{(9 - len(topic)) * ' '}{Style.BRIGHT}{Back.YELLOW}{Fore.WHITE} {topic.upper()} {Style.RESET_ALL}  "
        + message
    )
    print(msg)
