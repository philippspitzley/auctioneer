import os

from dotenv import load_dotenv


load_dotenv()

# DB variables
DB_USER = os.environ.get("DB_USER")
DB_PW = os.environ.get("DB_PW")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
# construct DB_URI, if host is 'localhost' password is not required and automatically omits
DB_URI = f"postgresql://{DB_USER}{'' if DB_HOST == 'localhost' else ':' + DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Security variables
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
