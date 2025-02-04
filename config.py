import os

from dotenv import load_dotenv


load_dotenv()

# DB variables
DB_USER: str = os.environ.get("DB_USER", "")
DB_PW: str = os.environ.get("DB_PW", "")
DB_HOST: str = os.environ.get("DB_HOST", "")
DB_PORT: str = os.environ.get("DB_PORT", "")
DB_NAME: str = os.environ.get("DB_NAME", "")
# construct DB_URI, if host is 'localhost' password is not required and automatically omits
DB_URI = f"postgresql://{DB_USER}{'' if DB_HOST == 'localhost' else ':' + DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Security variables
SECRET_KEY = os.environ.get("SECRET_KEY", None)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set! Please configure it as an environment variable."
    )
