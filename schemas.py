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


