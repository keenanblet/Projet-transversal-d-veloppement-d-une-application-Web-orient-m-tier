CREATE TABLE [dbo].[Entreprise] (
[siret] int NOT NULL,
[nom] nvarchar(50) NOT NULL,
PRIMARY KEY ([siret])
);

CREATE TABLE [dbo].[Vente] (
[id] int NOT NULL IDENTITY(1,1),
[quantité] int NOT NULL,
[prixPart] int NOT NULL,
[idEntreprise] int NOT NULL,
PRIMARY KEY ([id])
);

CREATE TABLE [dbo].[Part] (
[id] int NOT NULL IDENTITY(1,1),
[prix] int NOT NULL,
[idVente] int,
PRIMARY KEY ([id])
);

CREATE TABLE [dbo].[Commande] (
[id] int NOT NULL IDENTITY(1,1),
[idUser] int NOT NULL,
[idmoyenDePaiement] int NOT NULL,
[dateAchat] datetime DEFAULT (getdate()) NOT NULL,
[idEntreprise] int,
PRIMARY KEY ([id])
);

CREATE TABLE [dbo].[UserEntreprise] (
[idUser] int NOT NULL IDENTITY(1,1),
[idEntreprise] int NOT NULL,
PRIMARY KEY ([idUser], [idEntreprise])
);

CREATE TABLE [dbo].[LigneDeCommande] (
[id] int NOT NULL IDENTITY(1,1),
[prixAchat] int NOT NULL,
[Quantite] int NOT NULL,
[idCommande] int,
[idPart] int,
PRIMARY KEY ([id])
);

CREATE TABLE [dbo].[User] (
[id] int NOT NULL IDENTITY(1,1),
[nom] nvarchar(50) NOT NULL,
[prenom] nvarchar(50) NOT NULL,
[mail] nvarchar(100) NOT NULL,
[motDePasse] nvarchar(100) NOT NULL,
[estVendeur] binary(1) DEFAULT ((0)) NOT NULL,
PRIMARY KEY ([id])
);


ALTER TABLE [dbo].[Vente]
ADD CONSTRAINT [FK_3]
FOREIGN KEY ([idEntreprise]) 
REFERENCES [dbo].[Entreprise]([siret])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



ALTER TABLE [dbo].[Part]
ADD CONSTRAINT [FK_4]
FOREIGN KEY ([idVente]) 
REFERENCES [dbo].[Vente]([id])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



ALTER TABLE [dbo].[Commande]
ADD CONSTRAINT [FK_6]
FOREIGN KEY ([idUser]) 
REFERENCES [dbo].[User]([id])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



ALTER TABLE [dbo].[Commande]
ADD CONSTRAINT [FK_8]
FOREIGN KEY ([idEntreprise]) 
REFERENCES [dbo].[Entreprise]([siret])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



ALTER TABLE [dbo].[UserEntreprise]
ADD CONSTRAINT [FK_10]
FOREIGN KEY ([idEntreprise]) 
REFERENCES [dbo].[Entreprise]([siret])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



ALTER TABLE [dbo].[UserEntreprise]
ADD CONSTRAINT [FK_9]
FOREIGN KEY ([idUser]) 
REFERENCES [dbo].[User]([id])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



ALTER TABLE [dbo].[LigneDeCommande]
ADD CONSTRAINT [FK_7]
FOREIGN KEY ([idPart]) 
REFERENCES [dbo].[Part]([id])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



ALTER TABLE [dbo].[LigneDeCommande]
ADD CONSTRAINT [FK_5]
FOREIGN KEY ([idCommande]) 
REFERENCES [dbo].[Commande]([id])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



