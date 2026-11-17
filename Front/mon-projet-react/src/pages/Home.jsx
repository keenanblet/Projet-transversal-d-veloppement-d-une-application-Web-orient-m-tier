import { Link } from 'react-router-dom'
import { ArrowRight, Building2, ShieldCheck, TrendingUp, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const features = [
  {
    icon: TrendingUp,
    title: 'Investissez en parts',
    text: "Achetez des parts de sociétés en quelques clics et suivez vos investissements au même endroit.",
  },
  {
    icon: Building2,
    title: 'Placez votre société',
    text: "Dirigeants : mettez votre société en vente, voyez qui la finance et qui vous soutient.",
  },
  {
    icon: ShieldCheck,
    title: 'Transactions sécurisées',
    text: "Une même part ne peut jamais être vendue deux fois. Chaque achat est contrôlé.",
  },
  {
    icon: Clock,
    title: 'Historique horodaté',
    text: "L'heure exacte de chaque achat est enregistrée pour un suivi fiable.",
  },
]

const stats = [
  { value: '100%', label: 'Traçabilité' },
  { value: '3', label: 'Rôles utilisateurs' },
  { value: '24/7', label: 'Accès à la place de marché' },
]



export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b bg-background/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Link to="/" className="text-xl font-black tracking-tight">
            Ma<span className="text-primary">Part</span>
          </Link>
          <nav className="flex items-center gap-2">
            <Button variant="ghost" nativeButton={false} render={<Link to="/societes" />}>
              Sociétés
            </Button>
            <Button variant="ghost" nativeButton={false} render={<Link to="/connexion" />}>
              Connexion
            </Button>
            <Button nativeButton={false} render={<Link to="/inscription" />}>Créer un compte</Button>
          </nav>
        </div>
      </header>

      <section className="bg-foreground text-background">
        <div className="mx-auto max-w-6xl px-6 py-24 md:py-32">
          <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-primary">
            Marketplace de parts de sociétés
          </p>
          <h1 className="max-w-3xl text-4xl font-black leading-tight tracking-tight md:text-6xl">
            Achetez et vendez des parts.
            <span className="text-primary"> Simplement.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg text-background/70">
            MaPart met en relation investisseurs et dirigeants autour d'une place de marché
            claire, sécurisée et transparente.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Button size="lg" nativeButton={false} render={<Link to="/societes" />}>
              Voir les sociétés <ArrowRight />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-background/30 bg-transparent text-background hover:bg-background hover:text-foreground"
              nativeButton={false}
              render={<Link to="/inscription" />}
            >
              Créer un compte
            </Button>
          </div>
        </div>
        <div className="h-1.5 w-full bg-primary" />
      </section>

      <section className="border-b">
        <div className="mx-auto grid max-w-6xl grid-cols-1 divide-y px-6 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
          {stats.map((s) => (
            <div key={s.label} className="py-8 text-center sm:px-6">
              <div className="text-4xl font-black text-primary">{s.value}</div>
              <div className="mt-1 text-sm text-muted-foreground">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="text-3xl font-black tracking-tight">
          Pourquoi <span className="text-primary">MaPart</span> ?
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-2">
          {features.map(({ icon: Icon, title, text }) => (
            <Card key={title} className="transition-colors hover:border-primary">
              <CardHeader>
                <div className="mb-2 flex size-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Icon className="size-5" />
                </div>
                <CardTitle className="text-lg">{title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm">{text}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-20">
        <div className="flex flex-col items-start justify-between gap-6 rounded-2xl bg-primary p-10 text-primary-foreground md:flex-row md:items-center">
          <div>
            <h2 className="text-2xl font-black md:text-3xl">Prêt à investir ?</h2>
            <p className="mt-1 text-primary-foreground/80">
              Créez votre compte gratuitement et découvrez les sociétés disponibles.
            </p>
          </div>
          <Button size="lg" variant="secondary" nativeButton={false} render={<Link to="/inscription" />}>
            Commencer <ArrowRight />
          </Button>
        </div>
      </section>

      <footer className="border-t">
        <div className="mx-auto max-w-6xl px-6 py-6 text-sm text-muted-foreground">
          © {new Date().getFullYear()} MaPart — Projet transversal EPSI B2 - Keenan Johanne Palex
        </div>
      </footer>
    </div>
  )
}
