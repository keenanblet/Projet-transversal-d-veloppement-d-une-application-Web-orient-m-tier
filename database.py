# =============================================================================
# database.py : connexion à la base de données MySQL
# -----------------------------------------------------------------------------
# Ce fichier crée les 3 objets dont le reste du back a besoin :
#   - engine       : la connexion vers le serveur MySQL
#   - SessionLocal : une "fabrique" de sessions (une session = un échange avec la BDD)
#   - Base         : la classe mère de tous les modèles (voir models.py)
# =============================================================================

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()  # charge les variables du fichier .env

# Adresse de la BDD, au format : mysql://utilisateur:motdepasse@ip:port/nom_de_la_base
# Elle contient le mot de passe de la BDD : elle est rangée dans .env (non publié sur GitHub), pas dans le code.
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise RuntimeError("DB_URL manquant : ajoute-le dans le fichier .env")


# Moteur SQLAlchemy : c'est lui qui ouvre réellement les connexions vers MySQL.
# echo=True affiche dans le terminal toutes les requêtes SQL exécutées (pratique pour déboguer).
engine = create_engine(DB_URL,echo=True)

# Fabrique de sessions liée au moteur.
# autocommit=False : rien n'est enregistré en BDD tant qu'on n'appelle pas db.commit()
# autoflush=False  : SQLAlchemy n'envoie pas les changements en BDD de lui-même avant chaque requête
SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

# Classe de base : chaque modèle (ex : User dans models.py) en hérite,
# ce qui permet à SQLAlchemy de faire le lien entre une classe Python et une table SQL.
Base = declarative_base()
