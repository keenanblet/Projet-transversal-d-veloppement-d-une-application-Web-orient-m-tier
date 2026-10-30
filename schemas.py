from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserRead(BaseModel):
    id : int
    nom : str
    prenom : str
    mail : str
    motDePasse : str   
    estVendeur : bool


from pydantic import ConfigDict


class UserCrudRead(BaseModel):
    id: int
    nom: str
    prenom: str
    mail: str
    estVendeur: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    nom: str
    prenom: str
    mail: str
    motDePasse: str
    estVendeur: bool


class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    mail: Optional[str] = None
    motDePasse: Optional[str] = None
    estVendeur: Optional[bool] = None


