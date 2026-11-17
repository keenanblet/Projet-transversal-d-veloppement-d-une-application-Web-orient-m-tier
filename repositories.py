from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext


# hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import models,schemas


def get_users(db: Session, skip:int=0, limit: int=100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    data = user.model_dump()
    data["motDePasse"] = pwd_context.hash(user.motDePasse)
    db_user = models.User(**data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user is None:
        return None

    for field, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is None:
        return False

    db.delete(db_user)
    db.commit()
    return True

# cherche user avec son mail pour login 
def get_user_by_mail(db: Session, mail: str):
    return db.query(models.User).filter(models.User.mail == mail).first()

def get_entreprises(db: Session):
    resultat = []
    for e in db.query(models.Entreprise).all():
        vente = db.query(models.Vente).filter(models.Vente.idEntreprise == e.siret).first()
        resultat.append({
            "siret": e.siret,
            "nom": e.nom,
            "prixPart": vente.prixPart if vente else None,
        })
    return resultat


def acheter_parts(db: Session, siret: int, user_id: int, quantite: int):
    # parts de cette entreprise qui n'ont encore aucune ligne de commande
    parts = (
        db.query(models.Part)
        .join(models.Vente, models.Part.idVente == models.Vente.id)
        .outerjoin(models.LigneDeCommande, models.LigneDeCommande.idPart == models.Part.id)
        .filter(models.Vente.idEntreprise == siret, models.LigneDeCommande.id.is_(None))
        .with_for_update()  # verrou : évite qu'une même part soit vendue deux fois
        .limit(quantite)
        .all()
    )
    if len(parts) < quantite:
        db.rollback()
        return None

    commande = models.Commande(idUser=user_id, idmoyenDePaiement=1, idEntreprise=siret)
    db.add(commande)
    db.flush()  # pour récupérer commande.id
    for part in parts:
        db.add(models.LigneDeCommande(
            prixAchat=part.prix, Quantite=1, idCommande=commande.id, idPart=part.id
        ))
    db.commit()
    return commande