# =============================================================================
# schemas.py : les schémas Pydantic (= le format JSON qui entre et sort de l'API)
# -----------------------------------------------------------------------------
# FastAPI s'en sert pour :
#   - VALIDER ce que le front envoie (si un champ manque ou a le mauvais type -> erreur 422)
#   - FILTRER ce que l'API renvoie (avec response_model=..., seuls les champs listés sont envoyés)
# =============================================================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import Field
from pydantic import ConfigDict


# Utilisateur complet, MOT DE PASSE COMPRIS.
# Ne jamais l'utiliser comme response_model : le hash du mot de passe serait envoyé au front.
class UserRead(BaseModel):
    id : int
    nom : str
    prenom : str
    mail : str
    motDePasse : str
    estVendeur : bool


# Utilisateur tel qu'on le RENVOIE au front : sans le mot de passe.
# Utilisé comme response_model dans presque toutes les routes.
class UserCrudRead(BaseModel):
    id: int
    nom: str
    prenom: str
    mail: str
    estVendeur: bool

    # Permet de construire ce schéma directement à partir d'un objet SQLAlchemy (models.User)
    # en lisant ses attributs (user.nom, user.mail...) au lieu d'un dictionnaire.
    model_config = ConfigDict(from_attributes=True)


# Ce que le front envoie pour CRÉER un compte (page Inscription).
# Tous les champs sont obligatoires.
class UserCreate(BaseModel):
    nom: str
    prenom: str
    mail: str
    motDePasse: str      # reçu en clair, il est hashé dans repositories.create_user avant d'aller en BDD
    estVendeur: bool


# Ce que le front envoie pour MODIFIER un compte.
# Tous les champs sont optionnels : on n'envoie que ceux qu'on veut changer.
class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    mail: Optional[str] = None
    motDePasse: Optional[str] = None
    estVendeur: Optional[bool] = None


# Ce que le front envoie pour se connecter (page Connexion)
class LoginRequest(BaseModel):
    mail: str
    motDePasse: str

class EntrepriseRead(BaseModel):
    siret: int
    nom: str
    prixPart: Optional[int] = None
    partsRestantes: int = 0

MAX_PARTS_PAR_ACHAT = 10
class AchatCreate(BaseModel):
    quantite: int = Field(gt=0, le=MAX_PARTS_PAR_ACHAT)