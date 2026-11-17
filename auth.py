# =============================================================================
# auth.py : création et vérification des jetons JWT
# -----------------------------------------------------------------------------
# Principe :
#   1. au login, le back fabrique un jeton SIGNÉ avec une clé secrète (create_access_token)
#   2. ce jeton est rangé dans un cookie httpOnly (voir la route /login dans main.py)
#   3. à chaque requête, le back vérifie la signature du jeton (decode_access_token)
#      -> si quelqu'un modifie le jeton, la signature ne correspond plus et il est refusé
# Le contenu (payload) d'un JWT est LISIBLE par tous (il n'est pas chiffré) :
# on n'y met donc jamais d'information sensible, seulement l'id de l'utilisateur.
# =============================================================================

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()  # charge les variables du fichier .env dans os.environ

# Clé secrète qui signe les jetons. Quiconque la connaît peut fabriquer de faux jetons :
# elle reste dans .env (qui est dans le .gitignore) et ne doit jamais être publiée.
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    # on arrête le serveur dès le démarrage plutôt que d'avoir une erreur obscure au premier login
    raise RuntimeError("JWT_SECRET manquant : ajoute-le dans le fichier .env")

ALGORITHM = "HS256"                                            # algorithme de signature (HMAC + SHA-256)
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))   # durée de validité d'un jeton (60 min par défaut)

# Nom du cookie dans lequel le JWT est rangé
COOKIE_NAME = "access_token"
# Cookie "Secure" = envoyé uniquement en HTTPS.
# En local (http) : false ; en production (https) : mettre COOKIE_SECURE=true dans le .env
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


# Fabrique un jeton signé pour l'utilisateur donné
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),   # "subject" = à qui appartient le jeton (doit être une chaîne)
        "exp": expire,         # date d'expiration, vérifiée automatiquement par PyJWT
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Vérifie un jeton et renvoie l'id de l'utilisateur, ou None si le jeton n'est pas valable
def decode_access_token(token: str) -> int | None:
    try:
        # algorithms=[...] : on n'accepte QUE notre algorithme
        # (empêche l'attaque où un pirate envoie un jeton avec "alg": "none", donc non signé)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        return None   # jeton expiré
    except jwt.InvalidTokenError:
        return None   # jeton modifié / faux / mal formé
