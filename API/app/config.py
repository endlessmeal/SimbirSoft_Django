from starlette.config import Config
from dotenv import load_dotenv

load_dotenv()

config = Config(".env")

user_url = config("USER_SERVICE_URL")
messages_url = config("MESSAGES_SERVICE_URL")
goods_url = config("GOODS_SERVICE_URL")
monitor_url = config("MONITOR_SERVICE_URL")

redis_host = config("REDIS_HOST")
redis_port = config("REDIS_PORT")

token_ttl = config("TOKEN_TTL")
