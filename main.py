from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from database import Base, SessionLocal
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session

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
@user_router_v1.get("", summary="List all users", status_code=status.HTTP_200_OK, response_model=list[schemas.UserRead])
async def get_user_v1(db:Session=Depends(get_db)):
    try:
        users = repositories.get_users(db)
    except Exception:
        logger.exception("Database error while listing users")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    logger.info("Listed %d users", len(users))
    return users

# Create versioning for API endpoint by incorporating user_router_v1 into FastAPI application instance
app.include_router(user_router_v1, prefix="/v1")