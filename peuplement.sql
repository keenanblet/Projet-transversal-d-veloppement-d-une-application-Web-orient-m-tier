-- Peuplement idempotent (MariaDB) : marketplace de vente de parts de sociétés.
-- Chaque insertion utilise un identifiant fixe + INSERT IGNORE : relancer le script ne crée aucun doublon.
-- Note : idmoyenDePaiement n'a pas de table de référence dans le schéma (1 = CB, 2 = virement, 3 = PayPal).
-- Requiert MariaDB >= 10.2 (CTE récursive).

SET NAMES utf8mb4;

-- ------------------------------------------------------------
-- Schéma
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Entreprise` (
  `siret` INT NOT NULL,
  `nom` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`siret`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `User` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nom` VARCHAR(50) NOT NULL,
  `prenom` VARCHAR(50) NOT NULL,
  `mail` VARCHAR(100) NOT NULL,
  `motDePasse` VARCHAR(100) NOT NULL,
  `estVendeur` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Vente` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `quantité` INT NOT NULL,
  `prixPart` INT NOT NULL,
  `idEntreprise` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_3` FOREIGN KEY (`idEntreprise`) REFERENCES `Entreprise` (`siret`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Part` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `prix` INT NOT NULL,
  `idVente` INT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_4` FOREIGN KEY (`idVente`) REFERENCES `Vente` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Commande` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `idUser` INT NOT NULL,
  `idmoyenDePaiement` INT NOT NULL,
  `dateAchat` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idEntreprise` INT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_6` FOREIGN KEY (`idUser`) REFERENCES `User` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_8` FOREIGN KEY (`idEntreprise`) REFERENCES `Entreprise` (`siret`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `UserEntreprise` (
  `idUser` INT NOT NULL,
  `idEntreprise` INT NOT NULL,
  PRIMARY KEY (`idUser`, `idEntreprise`),
  CONSTRAINT `FK_9` FOREIGN KEY (`idUser`) REFERENCES `User` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_10` FOREIGN KEY (`idEntreprise`) REFERENCES `Entreprise` (`siret`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `LigneDeCommande` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `prixAchat` INT NOT NULL,
  `Quantite` INT NOT NULL,
  `idCommande` INT NULL,
  `idPart` INT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_5` FOREIGN KEY (`idCommande`) REFERENCES `Commande` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_7` FOREIGN KEY (`idPart`) REFERENCES `Part` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Entreprise (siret fixé)
-- ------------------------------------------------------------
INSERT IGNORE INTO `Entreprise` (`siret`, `nom`) VALUES
  (100000001, 'La P''tite Fabrik'),
  (100000002, 'Boulangerie Dupain'),
  (100000003, 'Brasserie du Nord'),
  (100000004, 'GreenTech Solutions'),
  (100000005, 'Atelier Vélo Cité'),
  (100000006, 'Domaine des Vignes Claires');

-- ------------------------------------------------------------
-- User (ids 1-3 : vendeurs, ids 4-8 : acheteurs)
-- motDePasse : valeurs factices (placeholder de hash), à ne jamais utiliser en production
-- ------------------------------------------------------------
INSERT IGNORE INTO `User` (`id`, `nom`, `prenom`, `mail`, `motDePasse`, `estVendeur`) VALUES
  (1, 'Martin',  'Claire', 'claire.martin@example.com',  '$2b$10$seedHashClaireMartin000000000000000000000000000000', 1),
  (2, 'Bernard', 'Julien', 'julien.bernard@example.com', '$2b$10$seedHashJulienBernard00000000000000000000000000000', 1),
  (3, 'Petit',   'Sophie', 'sophie.petit@example.com',   '$2b$10$seedHashSophiePetit0000000000000000000000000000000', 1),
  (4, 'Durand',  'Lucas',  'lucas.durand@example.com',   '$2b$10$seedHashLucasDurand0000000000000000000000000000000', 0),
  (5, 'Leroy',   'Emma',   'emma.leroy@example.com',     '$2b$10$seedHashEmmaLeroy000000000000000000000000000000000', 0),
  (6, 'Moreau',  'Hugo',   'hugo.moreau@example.com',    '$2b$10$seedHashHugoMoreau00000000000000000000000000000000', 0),
  (7, 'Simon',   'Léa',    'lea.simon@example.com',      '$2b$10$seedHashLeaSimon0000000000000000000000000000000000', 0),
  (8, 'Laurent', 'Thomas', 'thomas.laurent@example.com', '$2b$10$seedHashThomasLaurent000000000000000000000000000000', 0);

-- ------------------------------------------------------------
-- UserEntreprise (liaison vendeur <-> entreprise)
-- ------------------------------------------------------------
INSERT IGNORE INTO `UserEntreprise` (`idUser`, `idEntreprise`) VALUES
  (1, 100000001),
  (1, 100000004),
  (2, 100000002),
  (2, 100000003),
  (3, 100000005),
  (3, 100000006);

-- ------------------------------------------------------------
-- Vente (offres de parts : quantité, prix unitaire, entreprise émettrice)
-- ------------------------------------------------------------
INSERT IGNORE INTO `Vente` (`id`, `quantité`, `prixPart`, `idEntreprise`) VALUES
  (1, 10, 100, 100000001),
  (2, 20,  50, 100000002),
  (3,  5, 500, 100000003),
  (4, 15, 200, 100000004),
  (5,  8, 150, 100000005),
  (6, 12, 300, 100000006);

-- ------------------------------------------------------------
-- Part : une ligne par part, générée selon la quantité de chaque vente
-- Ids déterministes (ordre vente puis rang) => relançable sans doublon
-- ------------------------------------------------------------
INSERT IGNORE INTO `Part` (`id`, `prix`, `idVente`)
WITH RECURSIVE nums (n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM nums WHERE n < 20
)
SELECT
  ROW_NUMBER() OVER (ORDER BY v.`id`, nums.n) AS id,
  v.`prixPart`,
  v.`id`
FROM `Vente` v
JOIN nums ON nums.n <= v.`quantité`
WHERE v.`id` BETWEEN 1 AND 6;

-- ------------------------------------------------------------
-- Commande (idmoyenDePaiement : 1 = CB, 2 = virement, 3 = PayPal)
-- ------------------------------------------------------------
INSERT IGNORE INTO `Commande` (`id`, `idUser`, `idmoyenDePaiement`, `dateAchat`, `idEntreprise`) VALUES
  (1, 4, 1, '2026-09-01 10:15:00', 100000001),
  (2, 5, 2, '2026-09-05 14:30:00', 100000002),
  (3, 6, 3, '2026-09-12 09:00:00', 100000003),
  (4, 7, 1, '2026-09-20 16:45:00', 100000004),
  (5, 8, 1, '2026-10-02 11:20:00', 100000005),
  (6, 4, 2, '2026-10-15 18:05:00', 100000006);

-- ------------------------------------------------------------
-- LigneDeCommande (une ligne = une part achetée, au prix de la part)
-- Parts : vente 1 = ids 1-10, vente 2 = 11-30, vente 3 = 31-35, vente 4 = 36-50, vente 5 = 51-58, vente 6 = 59-70
-- ------------------------------------------------------------
INSERT IGNORE INTO `LigneDeCommande` (`id`, `prixAchat`, `Quantite`, `idCommande`, `idPart`) VALUES
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
  (11, 300, 1, 6, 60);
