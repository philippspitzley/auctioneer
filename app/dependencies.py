from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from .auth_handler import get_current_admin, get_current_user
from .db import get_session

# function dependencies
SessionDep = Annotated[Session, Depends(get_session)]

# path dependencies
UserRequired = Depends(get_current_user)
AdminRequired = Depends(get_current_admin)
