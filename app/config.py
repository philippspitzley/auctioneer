import os

from colorama import Back, Fore, Style
from dotenv import load_dotenv

# TODO: use utils.pretty_print for all prints

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


# DB variables
DB_USER: str = os.environ.get("DB_USER", "")
DB_PW: str = os.environ.get("DB_PW", "")
DB_HOST: str = os.environ.get("DB_HOST", "")
DB_PORT: str = os.environ.get("DB_PORT", "")
DB_NAME: str = os.environ.get("DB_NAME", "")
# construct DB_URI, if host is 'localhost' password is not required and automatically omits
DB_URI = f"postgresql://{DB_USER}{'' if DB_HOST == 'localhost' else ':' + DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Email variables
EMAIL_USER = os.environ.get("EMAIL_USER", None)
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", None)

if not EMAIL_USER or not EMAIL_PASSWORD:
    message = (
        f"  {Style.BRIGHT}{Fore.WHITE}{Back.RED} WARNING {Style.RESET_ALL}  "
        f"{Style.BRIGHT}{Fore.RED}EMAIL_USER{Style.NORMAL} and / or "
        f"{Style.BRIGHT}EAMIL_PASSWORD{Style.NORMAL} are not set! "
        "Please configure them as environment variables."
    )
    print(message)
