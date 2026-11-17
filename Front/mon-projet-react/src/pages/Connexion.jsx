import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { CircleXIcon } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useAuth } from '@/context/useAuth'

const initialForm = {
  mail: '',
  motDePasse: '',
}

export default function Connexion() {
  const [estActive, setEstActive] = useState(false)
  const { login } = useAuth()

  const navigate = useNavigate()
  const [form, setForm] = useState(initialForm)
  const update = (field) => (e) =>
    setForm((f) => ({
      ...f,
      [field]: e.target.value,
    }))

  async function handleSubmit(e) {
    e.preventDefault()
    try {
      await login(form.mail, form.motDePasse)
      navigate('/societes')
    } catch {
      setEstActive(true)
    }
  }


  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
      <Card className="w-full max-w-md">
        <CardHeader>
          <Link to="/" className="text-xl font-black tracking-tight">
            Ma<span className="text-primary">Part</span>
          </Link>
          <CardTitle className="mt-2 text-2xl">Connexion</CardTitle>
          <CardDescription>
            Heureux de vous revoir ! Connectez-vous à votre compte.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="mail">Email</Label>
              <Input
                id="mail"
                type="email"
                required
                placeholder="vous@exemple.com"
                autoComplete="email"
                value={form.mail}
                onChange={update('mail')}
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="motDePasse">Mot de passe</Label>
                <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                  Mot de passe oublié ?
                </a>
              </div>
              <Input
                id="motDePasse"
                type="password"
                required
                placeholder="••••••••"
                autoComplete="current-password"
                value={form.motDePasse}
                onChange={update('motDePasse')}
              />
            </div>
            <Button type="submit" className="w-full">
              Se connecter
            </Button>
            {estActive && (
              <Alert>
                <CircleXIcon />
                <AlertTitle>Connexion impossible</AlertTitle>
                <AlertDescription>
                  Mail ou mot de passe incorrect.
                </AlertDescription>
              </Alert>
            )}
          </form>
        </CardContent>
        <CardFooter className="justify-center text-sm text-muted-foreground">
          Pas encore de compte ?&nbsp;
          <Link to="/inscription" className="font-medium text-primary hover:underline">
            Créer un compte
          </Link>
        </CardFooter>
      </Card>
    </div>
  )
}
