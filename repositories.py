# =============================================================================
# repositories.py : toutes les opérations sur la BDD (requêtes SQLAlchemy)
# -----------------------------------------------------------------------------
# Les routes de main.py n'écrivent jamais de requête elles-mêmes : elles appellent
# ces fonctions. Avantage : la logique BDD est à un seul endroit, facile à relire et à tester.
# Chaque fonction reçoit "db", la session ouverte par get_db() dans main.py.
# =============================================================================
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext


# Outil de hashage des mots de passe avec l'algorithme bcrypt.
#   - pwd_context.hash("mdp")         -> renvoie un hash (irréversible) à stocker en BDD
#   - pwd_context.verify("mdp", hash) -> True si le mot de passe correspond au hash
# deprecated="auto" : si on change d'algorithme un jour, les anciens hash seront signalés comme obsolètes.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import models,schemas


# Renvoie une liste d'utilisateurs (pagination : on saute "skip" lignes et on en prend "limit" au maximum)
def get_users(db: Session, skip:int=0, limit: int=100):
    return db.query(models.User).offset(skip).limit(limit).all()


# Renvoie l'utilisateur dont l'id correspond, ou None s'il n'existe pas
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# Crée un utilisateur en BDD et le renvoie (avec son id généré par la BDD)
def create_user(db: Session, user: schemas.UserCreate):
    data = user.model_dump()                                 # schéma Pydantic -> dictionnaire Python
    data["motDePasse"] = pwd_context.hash(user.motDePasse)   # on remplace le mdp en clair par son hash
    db_user = models.User(**data)                            # dictionnaire -> objet SQLAlchemy
    db.add(db_user)                                          # prépare l'INSERT
    db.commit()                                              # exécute et enregistre en BDD
    db.refresh(db_user)                                      # relit la ligne pour récupérer l'id généré
    return db_user


# Modifie un utilisateur. Renvoie l'utilisateur modifié, ou None s'il n'existe pas.
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user is None:
        return None

    # exclude_unset=True : on ne garde que les champs réellement envoyés par le front,
    # pour ne pas écraser les autres colonnes avec None
    data = user.model_dump(exclude_unset=True)

    # nouveau mot de passe : on le hashe, comme à la création (jamais de mdp en clair en BDD)
    if data.get("motDePasse"):
        data["motDePasse"] = pwd_context.hash(data["motDePasse"])
    else:
        data.pop("motDePasse", None)  # mdp vide ou null : on garde l'ancien

    for field, value in data.items():
        setattr(db_user, field, value)                       # équivaut à db_user.<field> = value

    db.commit()
    db.refresh(db_user)
    return db_user


# Supprime un utilisateur. Renvoie True si supprimé, False s'il n'existait pas.
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is None:
        return False

    db.delete(db_user)
    db.commit()
    return True


# Cherche un utilisateur par son mail (utilisé par la route /auth/login), ou None s'il n'existe pas
def get_user_by_mail(db: Session, mail: str):
    return db.query(models.User).filter(models.User.mail == mail).first()

def get_entreprises(db: Session):
    resultat = []
    for e in db.query(models.Entreprise).all():
        vente = db.query(models.Vente).filter(models.Vente.idEntreprise == e.siret).first()
        # parts encore à vendre = parts de cette entreprise sans ligne de commande
        # (même requête que dans acheter_parts, mais on compte au lieu de récupérer)
        restantes = (
            db.query(models.Part)
            .join(models.Vente, models.Part.idVente == models.Vente.id)
            .outerjoin(models.LigneDeCommande, models.LigneDeCommande.idPart == models.Part.id)
            .filter(models.Vente.idEntreprise == e.siret, models.LigneDeCommande.id.is_(None))
            .count()
        )
        resultat.append({
            "siret": e.siret,
            "nom": e.nom,
            "prixPart": vente.prixPart if vente else None,
            "partsRestantes": restantes,
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
