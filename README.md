# Marketplace d'achat de part en bourse ou de parts de société
Liste de rôles

## Rôles

- User -> Acheter des parts
- Patron -> Voir le financement et qui aide, plus ajouter une société 
- Super admin -> dashboard de tous les projets

## Règles de gestions :

- Gestion d'une même part vendue deux fois
- Gestion de l'heure d'achat d'une part
- Une entreprise ne peux pas fermée si il y a des parts dedans

## Risques métiers en cas d’incident :

- plus de suivi des investissements (acheteurs et vendeurs)
- erreurs de paiments

## UserStroy :

- En tant que visiteur, je n'ai accès qu'à la partie vente de parts de socités
- En tant que user, j'ai également accès à la vente mais je peux aussi placer ma société pour avoir des parts
- En tant qu'admin, j'ai accès à l'integralité de la plate-forme (achat comme vente), ainsi qu'un dashboard spécial listant toutes les sociétés et tous les acheteurs

## Matrice des droits :

| Rôle | Voir les socités en ventes | Voir les acheteurs sur une société | Supprimer des sociétés | Ajouter une société | Acheter une part | Créer un compte | Supprimer son compte | Voir tous les comptes | Retirer sa mise sur des parts | Supprimer une société |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Admin | X | X | X | X |  | X | X | X |  | X |
| User | X | X | X | X | X | X | X |  | X | X |
| visiteur | X |  |  |  | X | X | X |  | X |  |

## Schéma UML
```mermaid
---
title : Schéma UML
---
classDiagram
		class User{
		    Id
		    Nom
		    Prénom
		    mail
		    MotDePasse
		    EstVendeur
		}
    class Entreprise{
        Id
        Nom
        Siret
    }
    
    class Part{
		    Id
		    Nom
		    Prix
		    
    }
    class Vente{
    Id
    Quantité
    }
    
    class Commande {
		    Id 
		    Moyen de paiement
		    

		    
    }
    
    class LigneCommande {
		    prix achat
		    quantité
    }
		
		
    
    
    User"1..*" --> "0..*" Entreprise
    User"0..1" --> "0..*" Part
    User"0..1" --> "0..*" Commande
    Entreprise"1" --> "0..*" Part
    Commande"1" --> "0..*" LigneCommande
    Part"1" --> "0..1" Commande
    Entreprise"1" --> "0..*" Vente
    Vente"1" --> "0..*" Part
```

## Installation des dépendances

Les commandes sont en **PowerShell**. Pour chaque dépendance : si la version requise est déjà installée, on n'installe pas, sinon on installe.

### 1. Outils système

| Outil | Version requise |
|:---|:---:|
| Node.js | >= 20 |
| Python | >= 3.10 |

```powershell
# Node.js >= 20
$nodeOk = $false
try { $nodeOk = ([version](node -v).TrimStart('v')).Major -ge 20 } catch {}
if ($nodeOk) { Write-Host "Node OK, pas d'installation" } else { winget install OpenJS.NodeJS.LTS }

# Python >= 3.10
$pyOk = $false
try { $pyOk = ([version](python --version).Split(' ')[1]) -ge [version]'3.10' } catch {}
if ($pyOk) { Write-Host "Python OK, pas d'installation" } else { winget install Python.Python.3.12 }
```

Redémarrer le terminal après une installation.

### 2. Back (FastAPI) : à la racine du projet

| Paquet | Version |
|:---|:---:|
| fastapi | >= 0.110 |
| uvicorn | >= 0.29 |
| sqlalchemy | >= 2.0 |
| mysqlclient | >= 2.2 |
| pydantic | >= 2.0 |
| email-validator | >= 2.0 |
| passlib | 1.7.4 |
| bcrypt | 4.0.1 (exactement, passlib est incompatible avec bcrypt >= 5) |

```powershell
function Install-PipIfNeeded($name, $min, $exact = $false) {
    $line = pip show $name 2>$null | Select-String '^Version:'
    if ($line) {
        $v = [version]($line.ToString().Split(':')[1].Trim())
        $ok = if ($exact) { $v -eq [version]$min } else { $v -ge [version]$min }
        if ($ok) { Write-Host "$name $v OK, pas d'installation"; return }
    }
    if ($exact) { pip install "$name==$min" } else { pip install "$name>=$min" }
}

Install-PipIfNeeded fastapi 0.110
Install-PipIfNeeded uvicorn 0.29
Install-PipIfNeeded sqlalchemy 2.0
Install-PipIfNeeded mysqlclient 2.2
Install-PipIfNeeded pydantic 2.0
Install-PipIfNeeded email-validator 2.0
Install-PipIfNeeded passlib 1.7.4 $true
Install-PipIfNeeded bcrypt 4.0.1 $true
```

Lancer l'API : `uvicorn main:app --reload`

### 3. Axios (racine du projet)

```powershell
$ax = npm ls axios --depth=0 2>$null | Select-String 'axios@(\d+)'
if ($ax -and [int]$ax.Matches[0].Groups[1].Value -ge 1) { Write-Host "axios OK, pas d'installation" } else { npm install }
```

### 4. Front (React + Vite) : dossier `Front/mon-projet-react`

| Paquet | Version |
|:---|:---:|
| react / react-dom | ^19 |
| react-router-dom | ^7 |
| @tanstack/react-query | ^5 |
| tailwindcss / @tailwindcss/vite | ^4 |
| @base-ui/react | ^1 |
| shadcn | ^4 |
| lucide-react | ^1 |
| class-variance-authority | ^0.7 |
| cn | ^0.5 |
| tw-animate-css | ^1 |
| @fontsource-variable/geist | ^5 |
| vite | ^8 (dev) |
| @vitejs/plugin-react | ^6 (dev) |
| eslint + plugins, globals, @types/react(-dom) | voir package.json (dev) |

Les versions exactes sont dans `package.json` : `npm install` ne retélécharge que ce qui est absent ou pas à la bonne version.

```powershell
cd Front/mon-projet-react
npm ls --depth=0 --silent 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "Toutes les dépendances sont à la bonne version, pas d'installation" } else { npm install }
npm run dev
```



``` mermaid
flowchart TB
  subgraph FRONT["⚛️ FRONT React - localhost:5173"]
    direction TB
    HTML["<b>index.html</b><br/>seule page HTML du site<br/>contient la div root où React dessine tout"]
    MAIN["<b>main.jsx</b><br/>point d'entrée React<br/>emboîte Router, AuthProvider puis App"]
    APP["<b>App.jsx</b><br/>table des routes<br/>associe chaque URL à une page"]
    HOME["<b>pages/Home.jsx</b><br/>page d'accueil, vitrine du site<br/>nav à adapter selon user connecté"]
    INS["<b>pages/Inscription.jsx</b><br/>formulaire de création de compte<br/>envoie POST /v1/users"]
    CON["<b>pages/Connexion.jsx</b><br/>formulaire mail + mot de passe<br/>appelle login() du contexte"]
    CTX["<b>context/AuthContext.jsx</b><br/>mémoire partagée de la connexion<br/>user, chargement, login(), logout()<br/>au démarrage demande /me au back"]
    UA["<b>context/useAuth.js</b><br/>raccourci pour lire le contexte<br/>depuis n'importe quelle page"]
    REQ["<b>components/ui/RequireAuth.jsx</b><br/>cache une page si pas connecté<br/>redirige vers /connexion<br/>pas encore utilisé"]
    UI["<b>components/ui/*</b><br/>composants shadcn<br/>Button, Card, Input, Alert..."]
    API["<b>lib/api.js</b><br/>client axios unique vers le back<br/>withCredentials : envoie le cookie"]
    FENV["<b>.env front</b><br/>VITE_API_URL<br/>adresse du back, rien de secret"]
    VITE["<b>vite.config.js</b><br/>serveur de dev + plugins React et Tailwind<br/>alias @ = dossier src"]

    HTML --> MAIN --> APP
    APP --> HOME & INS & CON
    MAIN --> CTX
    HOME & CON & REQ --> UA --> CTX
    CTX --> API
    INS --> API
    FENV -.-> API
    HOME & INS & CON -.-> UI
  end

  subgraph BACK["🐍 BACK FastAPI - localhost:8000"]
    direction TB
    MAINPY["<b>main.py</b><br/>point d'entrée de l'API<br/>CORS, logs, toutes les routes<br/>/v1/auth et /v1/users"]
    DEPS["<b>dépendances dans main.py</b><br/>get_db : ouvre et ferme la BDD<br/>get_current_user : lit le cookie, 401 sinon<br/>require_vendeur et verifier_proprietaire : 403"]
    AUTH["<b>auth.py</b><br/>fabrique et vérifie les JWT<br/>signés avec la clé secrète"]
    REPO["<b>repositories.py</b><br/>toutes les requêtes SQL<br/>get, create, update, delete<br/>hash et vérif bcrypt des mots de passe"]
    SCH["<b>schemas.py</b><br/>format du JSON entrant et sortant<br/>valide les données reçues<br/>UserCrudRead : jamais le mot de passe"]
    MOD["<b>models.py</b><br/>la table User vue depuis Python<br/>une Column = une colonne"]
    DBPY["<b>database.py</b><br/>connexion MySQL<br/>engine, SessionLocal, Base"]
    BENV["<b>.env back</b><br/>JWT_SECRET, DB_URL<br/>secrets, jamais sur GitHub"]
    REQS["<b>requirements.txt</b><br/>bibliothèques Python à installer"]

    MAINPY --> DEPS
    DEPS --> AUTH
    MAINPY --> REPO --> MOD --> DBPY
    MAINPY -.-> SCH
    BENV -.-> AUTH
    BENV -.-> DBPY
  end

  subgraph BDD["🗄️ BDD MySQL"]
    SQL[("<b>table User</b><br/>id, nom, prenom, mail<br/>motDePasse hashé, estVendeur")]
    SQLF["<b>v1__.sql / v2__.sql</b><br/>création des tables<br/><b>peuplement.sql</b><br/>données de test"]
    SQLF -.-> SQL
  end

  API == "requêtes HTTP + cookie httpOnly" ==> MAINPY
  DBPY == "requêtes SQL" ==> SQL

```