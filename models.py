from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from database import Base

# We import Base which is created from database.py 
class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    mail = Column(String)
    motDePasse = Column(String)    
    estVendeur = Column(Boolean)
    
class Entreprise(Base):
    __tablename__ = "Entreprise"
    siret = Column(Integer, primary_key=True)
    nom = Column(String)

class Vente(Base):
    __tablename__ = "Vente"
    id = Column(Integer, primary_key=True)
    quantite = Column("quantité", Integer)
    prixPart = Column(Integer)
    idEntreprise = Column(Integer, ForeignKey("Entreprise.siret"))

class Part(Base):
    __tablename__ = "Part"
    id = Column(Integer, primary_key=True)
    prix = Column(Integer)
    idVente = Column(Integer, ForeignKey("Vente.id"))

class Commande(Base):
    __tablename__ = "Commande"
    id = Column(Integer, primary_key=True)
    idUser = Column(Integer, ForeignKey("User.id"))
    idmoyenDePaiement = Column(Integer)
    idEntreprise = Column(Integer, ForeignKey("Entreprise.siret"))

class LigneDeCommande(Base):
    __tablename__ = "LigneDeCommande"
    id = Column(Integer, primary_key=True)
    prixAchat = Column(Integer)
    Quantite = Column(Integer)
    idCommande = Column(Integer, ForeignKey("Commande.id"))
    idPart = Column(Integer, ForeignKey("Part.id"))
    
#[id] int NOT NULL IDENTITY(1,1),
#[nom] nvarchar(50) NOT NULL,
#[prenom] nvarchar(50) NOT NULL,
#[mail] nvarchar(100) NOT NULL,
#[motDePasse] nvarchar(100) NOT NULL,
#[estVendeur] binary(1) DEFAULT ((0)) NOT NULL,