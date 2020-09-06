import os
from dotenv import load_dotenv

load_dotenv()

DATABASE = {
    "NAME": os.getenv("DATABASE"),
    "USER": os.getenv("USER"),
    "PASSWORD": os.getenv("PASSWORD"),
    "HOST": os.getenv("HOST"),
    "PORT": os.getenv("PORT"),
    "DATABASE": os.getenv("DATABASE"),
}


JWT = {
    "SECRET": os.getenv("SECRET"),
    "ALGORITHM": os.getenv("ALGORITHM"),
}

REDIS = {"HOST": os.getenv("REDIS_HOST"), "PORT": os.getenv("REDIS_PORT")}
