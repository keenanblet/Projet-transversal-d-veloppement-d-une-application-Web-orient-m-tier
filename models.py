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
    
    
    
#[id] int NOT NULL IDENTITY(1,1),
#[nom] nvarchar(50) NOT NULL,
#[prenom] nvarchar(50) NOT NULL,
#[mail] nvarchar(100) NOT NULL,
#[motDePasse] nvarchar(100) NOT NULL,
#[estVendeur] binary(1) DEFAULT ((0)) NOT NULL,