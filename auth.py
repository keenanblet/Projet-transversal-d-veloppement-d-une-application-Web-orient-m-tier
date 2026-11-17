import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()  # lit le fichier .env

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET manquant : ajoute-le dans le fichier .env")

ALGORITHM = "HS256"
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# cookie dans lequel le JWT est rangé
COOKIE_NAME = "access_token"
# en local (http) : false ; en production (https) : true
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),   # "subject" = à qui appartient le jeton (doit être une chaîne)
        "exp": expire,         # date d'expiration, vérifiée automatiquement par PyJWT
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        return None   # jeton expiré
    except jwt.InvalidTokenError:
        return None   # jeton modifié / faux / mal formé
