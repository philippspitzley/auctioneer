from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from .db import get_session
from .utils.auth import get_current_admin, get_current_user

# function dependencies
SessionDep = Annotated[Session, Depends(get_session)]

# path dependencies
UserRequired = Depends(get_current_user)
AdminRequired = Depends(get_current_admin)
