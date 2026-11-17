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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

#create FastAPI application instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# Log every request with its status code and duration
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("--> %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("<-- %s %s failed", request.method, request.url.path)
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("<-- %s %s %s (%.1f ms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


def get_db():
    db = SessionLocal()
    try : 
        yield db
    finally:
        db.close()

# identifie qui appelle, grâce au JWT rangé dans le cookie httpOnly "access_token"
# (le nom du paramètre doit être identique au nom du cookie)
def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if access_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non connecté")
    user_id = auth.decode_access_token(access_token)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou expiré")
    user = repositories.get_user(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable")
    return user

# refuse si estVendeur est faux
def require_vendeur(user = Depends(get_current_user)):
    if not user.estVendeur:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Réservé aux vendeurs")
    return user

# Create routers for different route groups
user_router_v1 = APIRouter(prefix="/users", tags=["users v1"])

'''
 -  Here we injected schemas / serializer from userRead to response since this can 
    show more than one user result we put use list 
 -  We create a simple repository to perform database process here
 -  Last we put proper http status using status_code decorator.
    Common status codes in the status module:
    status.HTTP_200_OK (default for successful responses)
    status.HTTP_201_CREATED
    status.HTTP_204_NO_CONTENT
    status.HTTP_400_BAD_REQUEST
    status.HTTP_404_NOT_FOUND
    status.HTTP_500_INTERNAL_SERVER_ERROR

'''


@user_router_v1.get("", summary="List all users", status_code=status.HTTP_200_OK, response_model=list[schemas.UserCrudRead])
async def get_user_v1(db:Session=Depends(get_db), x_token: str = Header()):
    try:
        users = repositories.get_users(db)
    except Exception:
        logger.exception("Database error while listing users")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    logger.info("Listed %d users", len(users))
    return users


@user_router_v1.get("/{user_id}", response_model=schemas.UserCrudRead, summary="Get a user by ID")
async def get_user_by_id_v1(user_id: int, db: Session = Depends(get_db)):
    user = repositories.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user




@user_router_v1.post("", response_model=schemas.UserCrudRead, status_code=status.HTTP_201_CREATED, summary="Create a user")
async def create_user_v1(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return repositories.create_user(db, user)


@user_router_v1.patch("/{user_id}", response_model=schemas.UserCrudRead, summary="Update a user")
async def update_user_v1(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = repositories.update_user(db, user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@user_router_v1.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
async def delete_user_v1(user_id: int, db: Session = Depends(get_db)):
    deleted = repositories.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# vérifie mail + mdp, pose le JWT dans un cookie httpOnly et renvoie le user (sans mdp ni jeton)
@auth_router.post("/login", response_model=schemas.UserCrudRead)
async def login(data: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = repositories.get_user_by_mail(db, data.mail)
    try:
        mdp_ok = user is not None and repositories.pwd_context.verify(data.motDePasse, user.motDePasse)
    except ValueError:
        # mdp en BDD qui n'est pas un hash bcrypt valide (ex : données de test en clair)
        mdp_ok = False
    if not mdp_ok:
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

# le JS ne peut pas toucher un cookie httpOnly : c'est le back qui le supprime
@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(
        key=auth.COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=auth.COOKIE_SECURE,
    )

# renvoie l'utilisateur connecté (401 sinon) : le front l'appelle pour savoir s'il est connecté
@auth_router.get("/me", response_model=schemas.UserCrudRead)
async def me(user = Depends(get_current_user)):
    return user

app.include_router(auth_router, prefix="/v1")

# Create versioning for API endpoint by incorporating user_router_v1 into FastAPI application instance
app.include_router(user_router_v1, prefix="/v1")