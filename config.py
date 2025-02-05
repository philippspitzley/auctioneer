import os
import warnings
from colorama import Back, Style, Fore

from dotenv import load_dotenv


load_dotenv()

# Security variables
SECRET_KEY = os.environ.get("SECRET_KEY", None)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    message = (
        f"  {Style.BRIGHT}{Fore.WHITE}{Back.RED} WARNING {Style.RESET_ALL}  "
        f"{Style.BRIGHT}{Fore.RED}SECRET_KEY{Style.NORMAL} is not set! "
        "Please configure it as an environment variable."
    )
    print(message)


# Admin variables
# email is currently used for username
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", None)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", None)

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    message = (
        f"  {Style.BRIGHT}{Fore.WHITE}{Back.RED} WARNING {Style.RESET_ALL}  "
        f"{Style.BRIGHT}{Fore.RED}ADMIN_USERNAME{Style.NORMAL} and "
        f"{Style.BRIGHT}ADMIN_PASSWORD{Style.NORMAL} are not set! "
        "Please configure them as environment variables."
    )
    print(message)


# DB variables
DB_USER: str = os.environ.get("DB_USER", "")
DB_PW: str = os.environ.get("DB_PW", "")
DB_HOST: str = os.environ.get("DB_HOST", "")
DB_PORT: str = os.environ.get("DB_PORT", "")
DB_NAME: str = os.environ.get("DB_NAME", "")
# construct DB_URI, if host is 'localhost' password is not required and automatically omits
DB_URI = f"postgresql://{DB_USER}{'' if DB_HOST == 'localhost' else ':' + DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
