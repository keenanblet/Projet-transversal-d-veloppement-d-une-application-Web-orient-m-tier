import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Building2,
  CheckCircle2,
  CircleXIcon,
  LogIn,
  LogOut,
  Minus,
  Plus,
  Search,
  ShoppingCart,
} from 'lucide-react'
import { api } from '@/lib/api'
import { useAuth } from '@/context/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

// Formate un prix en euros : 1500 -> "1 500 €"
const euros = (n) =>
  n == null
    ? '—'
    : new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n)

// Formate un SIRET par blocs : 12345678900012 -> "123 456 789 00012"
const formatSiret = (s) => String(s).replace(/^(\d{3})(\d{3})(\d{3})(\d+)$/, '$1 $2 $3 $4')

// Initiales affichées dans la pastille de la carte : "Ma Société" -> "MS"
const initiales = (nom) =>
  nom
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((m) => m[0].toUpperCase())
    .join('')

export default function Societes() {
  const { user, logout } = useAuth() // null si personne n'est connecté

  const [entreprises, setEntreprises] = useState([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState(false)
  const [recherche, setRecherche] = useState('')

  // achat en cours : l'entreprise choisie + la quantité (null = fenêtre fermée)
  const [achat, setAchat] = useState(null)
  const [envoi, setEnvoi] = useState(false)
  // message affiché après un achat : { ok: true/false, texte }
  const [resultat, setResultat] = useState(null)
  // nombre max de parts par achat, donné par le back (GET /v1/entreprises/regles)
  const [maxParAchat, setMaxParAchat] = useState(null)

  // récupère la limite une seule fois, au chargement de la page
  useEffect(() => {
    api
      .get('/v1/entreprises/regles')
      .then((res) => setMaxParAchat(res.data.maxPartsParAchat))
      .catch((err) => console.error(err))
  }, [])

  // charge la liste des sociétés (rappelée après un achat pour mettre à jour les parts restantes)
  function chargerEntreprises() {
    return api
      .get('/v1/entreprises')
      .then((res) => setEntreprises(res.data))
      .catch((err) => {
        console.error(err)
        setErreur(true)
      })
      .finally(() => setChargement(false))
  }

  useEffect(() => {
    chargerEntreprises()
  }, [])

  // filtre par nom ou SIRET
  const visibles = useMemo(() => {
    const q = recherche.trim().toLowerCase()
    if (!q) return entreprises
    return entreprises.filter(
      (e) => e.nom.toLowerCase().includes(q) || String(e.siret).includes(q.replace(/\s/g, ''))
    )
  }, [entreprises, recherche])

  function changerQuantite(delta) {
    setAchat((a) => {
      let q = Math.max(1, a.quantite + delta) // pas en dessous de 1
      if (maxParAchat != null) q = Math.min(q, maxParAchat) // pas au-dessus de la limite du back
      q = Math.min(q, a.entreprise.partsRestantes) // pas plus que ce qui reste en vente
      return { ...a, quantite: q }
    })
  }

  async function confirmerAchat() {
    setEnvoi(true)
    try {
      // le cookie JWT est envoyé automatiquement (withCredentials dans lib/api.js)
      const res = await api.post(`/v1/entreprises/${achat.entreprise.siret}/achats`, {
        quantite: achat.quantite,
      })
      setResultat({
        ok: true,
        texte: `${achat.quantite} part(s) de ${achat.entreprise.nom} achetée(s). Commande n°${res.data.idCommande}.`,
      })
    } catch (err) {
      // erreur 409 : detail est un texte / erreur 422 (validation Pydantic) : detail est une liste
      const detail = err.response?.data?.detail
      setResultat({
        ok: false,
        texte:
          typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
              ? `Quantité invalide (maximum ${maxParAchat ?? '?'} parts par achat).`
              : 'Achat impossible, réessayez plus tard.',
      })
    } finally {
      setEnvoi(false)
      setAchat(null)
      chargerEntreprises() // le nombre de parts restantes a changé
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ---------- En-tête ---------- */}
      <header className="sticky top-0 z-10 border-b bg-background/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Link to="/" className="text-xl font-black tracking-tight">
            Ma<span className="text-primary">Part</span>
          </Link>
          <nav className="flex items-center gap-2">
            {user ? (
              <>
                <span className="hidden text-sm text-muted-foreground sm:inline">
                  Bonjour <span className="font-semibold text-foreground">{user.prenom}</span>
                </span>
                <Button variant="ghost" onClick={logout}>
                  <LogOut /> Déconnexion
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" nativeButton={false} render={<Link to="/" />}>Accueil</Button>

                <Button variant="ghost" nativeButton={false} render={<Link to="/connexion" />}>
                  Connexion
                </Button>
                <Button nativeButton={false} render={<Link to="/inscription" />}>Créer un compte</Button>

              </>
            )}
          </nav>
        </div>
      </header>

      {/* ---------- Bandeau titre + recherche ---------- */}
      <section className="bg-foreground text-background">
        <div className="mx-auto max-w-6xl px-6 py-14 md:py-20">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary">
            Place de marché
          </p>
          <h1 className="text-4xl font-black tracking-tight md:text-5xl">
            Les sociétés <span className="text-primary">disponibles</span>
          </h1>
          <p className="mt-4 max-w-xl text-background/70">
            Parcourez les sociétés qui ouvrent leur capital et investissez en quelques clics.
          </p>
          <div className="relative mt-8 max-w-md">
            <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              placeholder="Rechercher par nom ou SIRET…"
              className="h-11 bg-background pl-9 text-foreground"
            />
          </div>
        </div>
        <div className="h-1.5 w-full bg-primary" />
      </section>

      <main className="mx-auto max-w-6xl px-6 py-12">
        {/* Résultat du dernier achat */}
        {resultat && (
          <Alert className="mb-8" onClick={() => setResultat(null)}>
            {resultat.ok ? <CheckCircle2 className="text-primary" /> : <CircleXIcon />}
            <AlertTitle>{resultat.ok ? 'Achat confirmé' : 'Achat impossible'}</AlertTitle>
            <AlertDescription>{resultat.texte}</AlertDescription>
          </Alert>
        )}

        {/* Invitation à se connecter */}
        {!user && !chargement && !erreur && (
          <div className="mb-8 flex flex-col items-start justify-between gap-4 rounded-xl border border-dashed p-5 sm:flex-row sm:items-center">
            <p className="text-sm text-muted-foreground">
              Connectez-vous pour acheter des parts de ces sociétés.
            </p>
            <Button nativeButton={false} render={<Link to="/connexion" />}>
              <LogIn /> Se connecter
            </Button>
          </div>
        )}

        {!chargement && !erreur && (
          <p className="mb-4 text-sm text-muted-foreground">
            {visibles.length} société{visibles.length > 1 ? 's' : ''}
          </p>
        )}

        {/* Chargement : cartes grises animées */}
        {chargement && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-52 animate-pulse rounded-xl bg-muted" />
            ))}
          </div>
        )}

        {/* Erreur de chargement */}
        {erreur && (
          <Alert>
            <CircleXIcon />
            <AlertTitle>Impossible de charger les sociétés</AlertTitle>
            <AlertDescription>Vérifiez que l'API est bien lancée puis rechargez la page.</AlertDescription>
          </Alert>
        )}

        {/* Aucun résultat */}
        {!chargement && !erreur && visibles.length === 0 && (
          <div className="flex flex-col items-center rounded-xl border border-dashed py-16 text-center">
            <Building2 className="size-10 text-muted-foreground" />
            <p className="mt-4 font-semibold">Aucune société trouvée</p>
            <p className="text-sm text-muted-foreground">
              {recherche ? 'Essayez une autre recherche.' : "Aucune société n'est en vente pour le moment."}
            </p>
          </div>
        )}

        {/* Liste des sociétés */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {visibles.map((e) => (
            <Card key={e.siret} className="flex flex-col transition-colors hover:border-primary">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="flex size-11 shrink-0 items-center justify-center rounded-lg bg-primary font-black text-primary-foreground">
                    {initiales(e.nom)}
                  </div>
                  <div className="min-w-0">
                    <CardTitle className="truncate text-lg">{e.nom}</CardTitle>
                    <CardDescription className="font-mono text-xs">
                      SIRET {formatSiret(e.siret)}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex-1">
                <p className="text-xs uppercase tracking-wider text-muted-foreground">Prix d'une part</p>
                <p className="text-3xl font-black text-primary">{euros(e.prixPart)}</p>
                <p className="mt-3 text-sm text-muted-foreground">
                  {e.partsRestantes > 0 ? (
                    <>
                      <span className="font-semibold text-foreground">{e.partsRestantes}</span> part
                      {e.partsRestantes > 1 ? 's' : ''} restante{e.partsRestantes > 1 ? 's' : ''}
                    </>
                  ) : (
                    <span className="font-semibold text-destructive">Épuisé</span>
                  )}
                </p>
              </CardContent>
              <CardFooter>
                {user ? (
                  <Button
                    className="w-full"
                    size="lg"
                    disabled={e.prixPart == null || e.partsRestantes === 0}
                    onClick={() => setAchat({ entreprise: e, quantite: 1 })}
                  >
                    <ShoppingCart /> Acheter
                  </Button>
                ) : (
                  <Button className="w-full" size="lg" variant="outline" nativeButton={false} render={<Link to="/connexion" />}>
                    Se connecter pour acheter
                  </Button>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>
      </main>

      {/* ---------- Fenêtre de confirmation d'achat ---------- */}
      <Dialog open={achat !== null} onOpenChange={(ouvert) => !ouvert && !envoi && setAchat(null)}>
        {achat && (
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Acheter des parts</DialogTitle>
              <DialogDescription>
                {achat.entreprise.nom} · {euros(achat.entreprise.prixPart)} la part
              </DialogDescription>
            </DialogHeader>

            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <span className="text-sm font-medium">Quantité</span>
                {maxParAchat != null && (
                  <p className="text-xs text-muted-foreground">Maximum {maxParAchat} parts par achat</p>
                )}
              </div>
              <div className="flex items-center gap-3">
                <Button
                  size="icon"
                  variant="outline"
                  aria-label="Retirer une part"
                  disabled={achat.quantite <= 1}
                  onClick={() => changerQuantite(-1)}
                >
                  <Minus />
                </Button>
                <span className="w-8 text-center text-lg font-bold tabular-nums">{achat.quantite}</span>
                <Button
                  size="icon"
                  variant="outline"
                  aria-label="Ajouter une part"
                  disabled={
                    achat.quantite >= achat.entreprise.partsRestantes ||
                    (maxParAchat != null && achat.quantite >= maxParAchat)
                  }
                  onClick={() => changerQuantite(1)}
                >
                  <Plus />
                </Button>
              </div>
            </div>

            <div className="flex items-baseline justify-between">
              <span className="text-muted-foreground">Total</span>
              <span className="text-2xl font-black text-primary">
                {euros(achat.entreprise.prixPart * achat.quantite)}
              </span>
            </div>

            <DialogFooter>
              <Button variant="outline" disabled={envoi} onClick={() => setAchat(null)}>
                Annuler
              </Button>
              <Button disabled={envoi} onClick={confirmerAchat}>
                {envoi ? 'Achat en cours…' : "Confirmer l'achat"}
              </Button>
            </DialogFooter>
          </DialogContent>
        )}
      </Dialog>
    </div>
  )
}
