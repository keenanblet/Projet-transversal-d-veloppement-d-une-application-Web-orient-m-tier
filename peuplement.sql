-- Peuplement idempotent (T-SQL) : marketplace de vente de parts de sociétés.
-- Chaque insertion utilise un identifiant fixe + WHERE NOT EXISTS : relancer le script ne crée aucun doublon.
-- Prérequis : schéma créé par v2__.sql.
-- Note : idmoyenDePaiement n'a pas de table de référence dans le schéma (1 = CB, 2 = virement, 3 = PayPal).
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
[idUser] int NOT NULL,
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




SET NOCOUNT ON;

------------------------------------------------------------
-- Entreprise (siret fixé)
------------------------------------------------------------
INSERT INTO [dbo].[Entreprise] ([siret], [nom])
SELECT v.siret, v.nom
FROM (VALUES
    (100000001, N'La P''tite Fabrik'),
    (100000002, N'Boulangerie Dupain'),
    (100000003, N'Brasserie du Nord'),
    (100000004, N'GreenTech Solutions'),
    (100000005, N'Atelier Vélo Cité'),
    (100000006, N'Domaine des Vignes Claires')
) AS v(siret, nom)
WHERE NOT EXISTS (SELECT 1 FROM [dbo].[Entreprise] e WHERE e.[siret] = v.siret);

------------------------------------------------------------
-- User (ids 1-3 : vendeurs, ids 4-8 : acheteurs)
-- motDePasse : valeurs factices (placeholder de hash), à ne jamais utiliser en production
------------------------------------------------------------
SET IDENTITY_INSERT [dbo].[User] ON;

INSERT INTO [dbo].[User] ([id], [nom], [prenom], [mail], [motDePasse], [estVendeur])
SELECT v.id, v.nom, v.prenom, v.mail, v.mdp, v.estVendeur
FROM (VALUES
    (1, N'Martin',  N'Claire',  N'claire.martin@example.com',  N'$2b$10$seedHashClaireMartin000000000000000000000000000000', 0x01),
    (2, N'Bernard', N'Julien',  N'julien.bernard@example.com', N'$2b$10$seedHashJulienBernard00000000000000000000000000000', 0x01),
    (3, N'Petit',   N'Sophie',  N'sophie.petit@example.com',   N'$2b$10$seedHashSophiePetit0000000000000000000000000000000', 0x01),
    (4, N'Durand',  N'Lucas',   N'lucas.durand@example.com',   N'$2b$10$seedHashLucasDurand0000000000000000000000000000000', 0x00),
    (5, N'Leroy',   N'Emma',    N'emma.leroy@example.com',     N'$2b$10$seedHashEmmaLeroy000000000000000000000000000000000', 0x00),
    (6, N'Moreau',  N'Hugo',    N'hugo.moreau@example.com',    N'$2b$10$seedHashHugoMoreau00000000000000000000000000000000', 0x00),
    (7, N'Simon',   N'Léa',     N'lea.simon@example.com',      N'$2b$10$seedHashLeaSimon0000000000000000000000000000000000', 0x00),
    (8, N'Laurent', N'Thomas',  N'thomas.laurent@example.com', N'$2b$10$seedHashThomasLaurent000000000000000000000000000000', 0x00)
) AS v(id, nom, prenom, mail, mdp, estVendeur)
WHERE NOT EXISTS (SELECT 1 FROM [dbo].[User] u WHERE u.[id] = v.id OR u.[mail] = v.mail);

SET IDENTITY_INSERT [dbo].[User] OFF;

------------------------------------------------------------
-- UserEntreprise (liaison vendeur <-> entreprise ; idUser est IDENTITY dans le schéma)
------------------------------------------------------------
SET IDENTITY_INSERT [dbo].[UserEntreprise] ON;

INSERT INTO [dbo].[UserEntreprise] ([idUser], [idEntreprise])
SELECT v.idUser, v.idEntreprise
FROM (VALUES
    (1, 100000001),
    (1, 100000004),
    (2, 100000002),
    (2, 100000003),
    (3, 100000005),
    (3, 100000006)
) AS v(idUser, idEntreprise)
WHERE NOT EXISTS (
    SELECT 1 FROM [dbo].[UserEntreprise] ue
    WHERE ue.[idUser] = v.idUser AND ue.[idEntreprise] = v.idEntreprise
);

SET IDENTITY_INSERT [dbo].[UserEntreprise] OFF;

------------------------------------------------------------
-- Vente (offres de parts : quantité, prix unitaire, entreprise émettrice)
------------------------------------------------------------
SET IDENTITY_INSERT [dbo].[Vente] ON;

INSERT INTO [dbo].[Vente] ([id], [quantité], [prixPart], [idEntreprise])
SELECT v.id, v.quantite, v.prixPart, v.idEntreprise
FROM (VALUES
    (1, 10, 100, 100000001),
    (2, 20,  50, 100000002),
    (3,  5, 500, 100000003),
    (4, 15, 200, 100000004),
    (5,  8, 150, 100000005),
    (6, 12, 300, 100000006)
) AS v(id, quantite, prixPart, idEntreprise)
WHERE NOT EXISTS (SELECT 1 FROM [dbo].[Vente] x WHERE x.[id] = v.id);

SET IDENTITY_INSERT [dbo].[Vente] OFF;

------------------------------------------------------------
-- Part : une ligne par part, générée selon la quantité de chaque vente
-- Ids déterministes (ordre vente puis rang) => relançable sans doublon
------------------------------------------------------------
SET IDENTITY_INSERT [dbo].[Part] ON;

;WITH nums AS (
    SELECT TOP (20) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
    FROM sys.all_objects
),
parts AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY v.[id], n.n) AS id,
        v.[prixPart] AS prix,
        v.[id]       AS idVente
    FROM [dbo].[Vente] v
    JOIN nums n ON n.n <= v.[quantité]
    WHERE v.[id] BETWEEN 1 AND 6
)
INSERT INTO [dbo].[Part] ([id], [prix], [idVente])
SELECT p.id, p.prix, p.idVente
FROM parts p
WHERE NOT EXISTS (SELECT 1 FROM [dbo].[Part] x WHERE x.[id] = p.id);

SET IDENTITY_INSERT [dbo].[Part] OFF;

------------------------------------------------------------
-- Commande (idmoyenDePaiement : 1 = CB, 2 = virement, 3 = PayPal)
------------------------------------------------------------
SET IDENTITY_INSERT [dbo].[Commande] ON;

INSERT INTO [dbo].[Commande] ([id], [idUser], [idmoyenDePaiement], [dateAchat], [idEntreprise])
SELECT v.id, v.idUser, v.moyen, v.dateAchat, v.idEntreprise
FROM (VALUES
    (1, 4, 1, CONVERT(datetime, '2026-09-01T10:15:00', 126), 100000001),
    (2, 5, 2, CONVERT(datetime, '2026-09-05T14:30:00', 126), 100000002),
    (3, 6, 3, CONVERT(datetime, '2026-09-12T09:00:00', 126), 100000003),
    (4, 7, 1, CONVERT(datetime, '2026-09-20T16:45:00', 126), 100000004),
    (5, 8, 1, CONVERT(datetime, '2026-10-02T11:20:00', 126), 100000005),
    (6, 4, 2, CONVERT(datetime, '2026-10-15T18:05:00', 126), 100000006)
) AS v(id, idUser, moyen, dateAchat, idEntreprise)
WHERE NOT EXISTS (SELECT 1 FROM [dbo].[Commande] c WHERE c.[id] = v.id);

SET IDENTITY_INSERT [dbo].[Commande] OFF;

------------------------------------------------------------
-- LigneDeCommande (une ligne = une part achetée, au prix de la part)
-- Parts : vente 1 = ids 1-10, vente 2 = 11-30, vente 3 = 31-35, vente 4 = 36-50, vente 5 = 51-58, vente 6 = 59-70
------------------------------------------------------------
SET IDENTITY_INSERT [dbo].[LigneDeCommande] ON;

INSERT INTO [dbo].[LigneDeCommande] ([id], [prixAchat], [Quantite], [idCommande], [idPart])
SELECT v.id, v.prixAchat, v.quantite, v.idCommande, v.idPart
FROM (VALUES
    ( 1, 100, 1, 1,  1),
    ( 2, 100, 1, 1,  2),
    ( 3,  50, 1, 2, 11),
    ( 4,  50, 1, 2, 12),
    ( 5,  50, 1, 2, 13),
    ( 6, 500, 1, 3, 31),
    ( 7, 200, 1, 4, 36),
    ( 8, 200, 1, 4, 37),
    ( 9, 150, 1, 5, 51),
    (10, 300, 1, 6, 59),
    (11, 300, 1, 6, 60)
) AS v(id, prixAchat, quantite, idCommande, idPart)
WHERE NOT EXISTS (SELECT 1 FROM [dbo].[LigneDeCommande] l WHERE l.[id] = v.id);

SET IDENTITY_INSERT [dbo].[LigneDeCommande] OFF;


SELECT * from [Part]