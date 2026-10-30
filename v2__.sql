IF OBJECT_ID('dbo.Entreprise', 'U') IS NULL
CREATE TABLE [dbo].Entreprise (
[siret] int NOT NULL,
[nom] nvarchar(50) NOT NULL,
PRIMARY KEY ([siret])
);
IF OBJECT_ID('dbo.Vente', 'U') IS NULL
CREATE TABLE [dbo].[Vente] (
[id] int NOT NULL IDENTITY(1,1),
[quantité] int NOT NULL,
[prixPart] int NOT NULL,
[idEntreprise] int NOT NULL,
PRIMARY KEY ([id])
);
IF OBJECT_ID('dbo.Part', 'U') IS NULL
CREATE TABLE [dbo].[Part] (
[id] int NOT NULL IDENTITY(1,1),
[prix] int NOT NULL,
[idVente] int,
PRIMARY KEY ([id])
);
IF OBJECT_ID('dbo.Commande', 'U') IS NULL
CREATE TABLE [dbo].[Commande] (
[id] int NOT NULL IDENTITY(1,1),
[idUser] int NOT NULL,
[idmoyenDePaiement] int NOT NULL,
[dateAchat] datetime DEFAULT (getdate()) NOT NULL,
[idEntreprise] int,
PRIMARY KEY ([id])
);
IF OBJECT_ID('dbo.UserEntreprise', 'U') IS NULL
CREATE TABLE [dbo].[UserEntreprise] (
[idUser] int NOT NULL IDENTITY(1,1),
[idEntreprise] int NOT NULL,
PRIMARY KEY ([idUser], [idEntreprise])
);
IF OBJECT_ID('dbo.LigneDeCommande', 'U') IS NULL
CREATE TABLE [dbo].[LigneDeCommande] (
[id] int NOT NULL IDENTITY(1,1),
[prixAchat] int NOT NULL,
[Quantite] int NOT NULL,
[idCommande] int,
[idPart] int,
PRIMARY KEY ([id])
);
IF OBJECT_ID('dbo.User', 'U') IS NULL
CREATE TABLE [dbo].[User] (
[id] int NOT NULL IDENTITY(1,1),
[nom] nvarchar(50) NOT NULL,
[prenom] nvarchar(50) NOT NULL,
[mail] nvarchar(100) NOT NULL,
[motDePasse] nvarchar(100) NOT NULL,
[estVendeur] binary(1) DEFAULT ((0)) NOT NULL,
PRIMARY KEY ([id])
);

IF OBJECT_ID('dbo.FK_3', 'F') IS NULL
ALTER TABLE [dbo].[Vente]
ADD CONSTRAINT [FK_3]
FOREIGN KEY ([idEntreprise]) 
REFERENCES [dbo].[Entreprise]([siret])
ON DELETE CASCADE
ON UPDATE NO ACTION;



IF OBJECT_ID('dbo.FK_4', 'F') IS NULL
ALTER TABLE [dbo].[Part]
ADD CONSTRAINT [FK_4]
FOREIGN KEY ([idVente]) 
REFERENCES [dbo].[Vente]([id])
ON DELETE CASCADE
ON UPDATE NO ACTION;



IF OBJECT_ID('dbo.FK_6', 'F') IS NULL
ALTER TABLE [dbo].[Commande]
ADD CONSTRAINT [FK_6]
FOREIGN KEY ([idUser]) 
REFERENCES [dbo].[User]([id])
ON DELETE CASCADE
ON UPDATE NO ACTION;



IF OBJECT_ID('dbo.FK_8', 'F') IS NULL
ALTER TABLE [dbo].[Commande]
ADD CONSTRAINT [FK_8]
FOREIGN KEY ([idEntreprise]) 
REFERENCES [dbo].[Entreprise]([siret])
ON DELETE NO ACTION
ON UPDATE NO ACTION;



IF OBJECT_ID('dbo.FK_10', 'F') IS NULL
ALTER TABLE [dbo].[UserEntreprise]
ADD CONSTRAINT [FK_10]
FOREIGN KEY ([idEntreprise]) 
REFERENCES [dbo].[Entreprise]([siret])
ON DELETE CASCADE
ON UPDATE NO ACTION;



IF OBJECT_ID('dbo.FK_9', 'F') IS NULL
ALTER TABLE [dbo].[UserEntreprise]
ADD CONSTRAINT [FK_9]
FOREIGN KEY ([idUser]) 
REFERENCES [dbo].[User]([id])
ON DELETE CASCADE
ON UPDATE NO ACTION;



IF OBJECT_ID('dbo.FK_7', 'F') IS NULL
ALTER TABLE [dbo].[LigneDeCommande]
ADD CONSTRAINT [FK_7]
FOREIGN KEY ([idPart]) 
REFERENCES [dbo].[Part]([id])
ON DELETE CASCADE
ON UPDATE NO ACTION;



IF OBJECT_ID('dbo.FK_5', 'F') IS NULL
ALTER TABLE [dbo].[LigneDeCommande]
ADD CONSTRAINT [FK_5]
FOREIGN KEY ([idCommande]) 
REFERENCES [dbo].[Commande]([id])
ON DELETE CASCADE
ON UPDATE NO ACTION;



