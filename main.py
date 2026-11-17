# =============================================================================
# main.py : point d'entrée de l'API FastAPI
# -----------------------------------------------------------------------------
# Contient : la création de l'application, la configuration CORS, le log des requêtes,
# les dépendances (session BDD, utilisateur connecté, vendeur) et toutes les routes.
# Lancement : uvicorn main:app --reload   ->   documentation Swagger sur /docs
# =============================================================================

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, Response, status, Header, Cookie
from fastapi.middleware.cors import CORSMiddleware
import auth
from pydantic import BaseModel
from database import Base, SessionLocal
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware


import models,schemas, repositories
import logging
import time

# Configuration des logs affichés dans le terminal : date, niveau, nom du logger, message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

# Création de l'application FastAPI
app = FastAPI()

# CORS : autorise le front React (servi sur un autre port) à appeler l'API.
# Sans ça, le navigateur bloque les requêtes venant de localhost:5173 vers localhost:8000.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # adresses du front autorisées
    allow_methods=["*"],                                                # GET, POST, PATCH, DELETE...
    allow_headers=["*"],                                                # tous les en-têtes
    allow_credentials=True,  # autorise l'envoi des cookies (indispensable pour le cookie JWT)
                             # -> interdit d'utiliser "*" dans allow_origins
)


# Middleware : s'exécute autour de CHAQUE requête.
# Affiche dans le terminal la méthode, l'URL, le code de réponse et la durée de traitement.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("--> %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)   # on laisse FastAPI traiter la requête (exécuter la route)
    except Exception:
        logger.exception("<-- %s %s failed", request.method, request.url.path)
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("<-- %s %s %s (%.1f ms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


# =============================================================================
# DÉPENDANCES
# Fonctions injectées dans les routes avec Depends(...). FastAPI les exécute
# avant la route et lui passe leur résultat en paramètre.
# =============================================================================

# Ouvre une session BDD pour la durée d'une requête, puis la ferme quoi qu'il arrive.
# "yield" donne la session à la route ; le code après le yield s'exécute une fois la route terminée.
def get_db():
    db = SessionLocal()
    try :
        yield db
    finally:
        db.close()

# Identifie qui appelle, grâce au JWT rangé dans le cookie httpOnly "access_token".
# Le nom du paramètre doit être identique au nom du cookie : c'est comme ça que FastAPI le retrouve.
# Renvoie l'utilisateur connecté, ou lève une erreur 401 (= non authentifié).
# Utilisation dans une route : user = Depends(get_current_user)
def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    # pas de cookie -> l'utilisateur ne s'est pas connecté (ou s'est déconnecté)
    if access_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non connecté")
    # vérifie la signature et la date d'expiration du jeton
    user_id = auth.decode_access_token(access_token)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou expiré")
    # le jeton est valide, mais le compte existe-t-il encore ? (il a pu être supprimé entre-temps)
    user = repositories.get_user(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable")
    return user

# Comme get_current_user, mais refuse en plus les utilisateurs qui ne sont pas vendeurs (erreur 403 = interdit).
# estVendeur est lu en BDD : modifier les données côté front ne permet pas de tricher.
# Utilisation dans une route : user = Depends(require_vendeur)
def require_vendeur(user = Depends(get_current_user)):
    if not user.estVendeur:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Réservé aux vendeurs")
    return user


# =============================================================================
# ROUTES UTILISATEURS : /v1/users
# =============================================================================

# Routeur regroupant toutes les routes qui commencent par /users (tag "users v1" dans Swagger)
user_router_v1 = APIRouter(prefix="/users", tags=["users v1"])

'''
Rappels sur les routes :
 -  response_model : le schéma Pydantic utilisé pour la réponse. Il filtre les champs envoyés
    (UserCrudRead -> jamais le mot de passe). Une liste de schémas -> list[...]
 -  Les routes ne parlent pas directement à la BDD : elles passent par repositories.py
 -  status_code : le code HTTP renvoyé en cas de succès. Codes courants (module status) :
    status.HTTP_200_OK                    (succès, valeur par défaut)
    status.HTTP_201_CREATED               (ressource créée)
    status.HTTP_204_NO_CONTENT            (succès, réponse vide)
    status.HTTP_400_BAD_REQUEST           (requête incorrecte)
    status.HTTP_401_UNAUTHORIZED          (non connecté)
    status.HTTP_403_FORBIDDEN             (connecté mais pas le droit)
    status.HTTP_404_NOT_FOUND             (introuvable)
    status.HTTP_500_INTERNAL_SERVER_ERROR (erreur du serveur)
'''


# GET /v1/users : liste tous les utilisateurs (sans mot de passe). Réservé aux utilisateurs connectés.
# "_" : on n'utilise pas l'utilisateur, on veut seulement que get_current_user s'exécute (401 sinon).
@user_router_v1.get("", summary="List all users", status_code=status.HTTP_200_OK, response_model=list[schemas.UserCrudRead])
async def get_user_v1(db:Session=Depends(get_db), _ = Depends(get_current_user)):
    try:
        users = repositories.get_users(db)
    except Exception:
        # erreur BDD (serveur MySQL injoignable, etc.) : on la note dans les logs et on renvoie une 500
        logger.exception("Database error while listing users")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    logger.info("Listed %d users", len(users))
    return users


# GET /v1/users/{user_id} : renvoie un utilisateur par son id (404 s'il n'existe pas). Réservé aux utilisateurs connectés.
@user_router_v1.get("/{user_id}", response_model=schemas.UserCrudRead, summary="Get a user by ID")
async def get_user_by_id_v1(user_id: int, db: Session = Depends(get_db), _ = Depends(get_current_user)):
    user = repositories.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user




# POST /v1/users : crée un compte (page Inscription). Route publique, pas besoin d'être connecté.
# Le mot de passe est hashé dans repositories.create_user.
@user_router_v1.post("", response_model=schemas.UserCrudRead, status_code=status.HTTP_201_CREATED, summary="Create a user")
async def create_user_v1(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return repositories.create_user(db, user)


# Vérifie que l'utilisateur connecté agit bien sur SON propre compte (sinon 403 = interdit).
def verifier_proprietaire(current_user, user_id: int):
    if current_user.id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Vous ne pouvez modifier que votre propre compte")


# PATCH /v1/users/{user_id} : modifie un utilisateur (seuls les champs envoyés sont changés).
# Il faut être connecté ET être le propriétaire du compte.
@user_router_v1.patch("/{user_id}", response_model=schemas.UserCrudRead, summary="Update a user")
async def update_user_v1(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    verifier_proprietaire(current_user, user_id)
    updated_user = repositories.update_user(db, user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# DELETE /v1/users/{user_id} : supprime un utilisateur (réponse vide, code 204).
# Il faut être connecté ET être le propriétaire du compte.
# Le compte n'existant plus, on supprime aussi le cookie : l'utilisateur est déconnecté.
@user_router_v1.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
async def delete_user_v1(
    user_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    verifier_proprietaire(current_user, user_id)
    deleted = repositories.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    response.delete_cookie(
        key=auth.COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=auth.COOKIE_SECURE,
    )


# =============================================================================
# ROUTES D'AUTHENTIFICATION : /v1/auth
# =============================================================================

# Routeur regroupant les routes /auth (tag "auth" dans Swagger)
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# POST /v1/auth/login : vérifie mail + mdp, pose le JWT dans un cookie httpOnly
# et renvoie l'utilisateur (sans mot de passe ni jeton).
# "response: Response" donne accès à la réponse HTTP pour pouvoir y ajouter le cookie.
@auth_router.post("/login", response_model=schemas.UserCrudRead)
async def login(data: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = repositories.get_user_by_mail(db, data.mail)
    try:
        # verify() hashe le mdp reçu et le compare au hash stocké en BDD
        mdp_ok = user is not None and repositories.pwd_context.verify(data.motDePasse, user.motDePasse)
    except ValueError:
        # mdp en BDD qui n'est pas un hash bcrypt valide (ex : données de test en clair)
        mdp_ok = False
    if not mdp_ok:
        # même message que le mail soit inconnu ou le mdp faux :
        # on ne révèle pas à un pirate quels mails existent dans la BDD
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Mail ou mot de passe incorrect")
    token = auth.create_access_token(user.id)
    response.set_cookie(
        key=auth.COOKIE_NAME,
        value=token,
        httponly=True,                     # illisible par le JavaScript (protège du vol par XSS)
        samesite="lax",                    # limite les attaques CSRF
        secure=auth.COOKIE_SECURE,         # True en production (HTTPS obligatoire)
        max_age=auth.EXPIRE_MINUTES * 60,  # durée de vie en secondes, comme le JWT
    )
    return user

# POST /v1/auth/logout : déconnexion.
# Le JS ne peut pas toucher un cookie httpOnly : c'est le back qui le supprime.
# Les options (httponly, samesite, secure) doivent être les mêmes qu'à la création du cookie.
@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(
        key=auth.COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=auth.COOKIE_SECURE,
    )

# GET /v1/auth/me : renvoie l'utilisateur connecté (401 sinon).
# Le front l'appelle au chargement pour savoir si quelqu'un est connecté.
@auth_router.get("/me", response_model=schemas.UserCrudRead)
async def me(user = Depends(get_current_user)):
    return user


# =============================================================================
# ROUTES ENTREPRISES : /v1/entreprises
# =============================================================================

entreprise_router_v1 = APIRouter(prefix="/entreprises", tags=["entreprises v1"])

@entreprise_router_v1.get("/regles")
async def regles_v1():
    return {"maxPartsParAchat": schemas.MAX_PARTS_PAR_ACHAT}
# publique : un visiteur non connecté peut la lire
@entreprise_router_v1.get("", response_model=list[schemas.EntrepriseRead])
async def list_entreprises_v1(db: Session = Depends(get_db)):
    return repositories.get_entreprises(db)

# réservée aux connectés (cookie JWT, via get_current_user)
@entreprise_router_v1.post("/{siret}/achats", status_code=status.HTTP_201_CREATED)
async def acheter_parts_v1(
    siret: int,
    achat: schemas.AchatCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    commande = repositories.acheter_parts(db, siret, user.id, achat.quantite)
    if commande is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Pas assez de parts disponibles")
    return {"idCommande": commande.id}

# =============================================================================
# ENREGISTREMENT DES ROUTEURS
# Le préfixe /v1 versionne l'API : les URL finales sont /v1/auth/..., /v1/users/... et /v1/entreprises/...
# (si un jour l'API change, on pourra créer une /v2 sans casser les anciens clients)
# =============================================================================
app.include_router(auth_router, prefix="/v1")
app.include_router(user_router_v1, prefix="/v1")
app.include_router(entreprise_router_v1, prefix="/v1")
