from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.middleware.cors import CORSMiddleware
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

# identifie qui appelle, grâce au header X-User-Id 
def get_current_user(x_user_id: int = Header(), db: Session = Depends(get_db)):
    user = repositories.get_user(db, x_user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non connecté")
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

# renvoie le user avec id et estVendeur pas de mdp
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=schemas.UserCrudRead)
async def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = repositories.get_user_by_mail(db, data.mail)
    if user is None or not repositories.pwd_context.verify(data.motDePasse, user.motDePasse):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Mail ou mot de passe incorrect")
    return user

app.include_router(auth_router, prefix="/v1")

# Create versioning for API endpoint by incorporating user_router_v1 into FastAPI application instance
app.include_router(user_router_v1, prefix="/v1")