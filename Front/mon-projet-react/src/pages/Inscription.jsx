import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import axios from 'axios'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { useNavigate } from 'react-router-dom';
import { CircleXIcon, InfoIcon } from "lucide-react"
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"
import { api } from '@/lib/api'

const initialForm = {
  nom: '',
  prenom: '',
  mail: '',
  motDePasse: '',
  estVendeur: false,
}

export default function Inscription() {
  const [estActive, setEstActive] = useState(false);

  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm)
  const update = (field) => (e) =>
    setForm((f) => ({
      ...f,
      [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value,
    }))

  function handleSubmit(e) {
    e.preventDefault()
    api.post('/v1/users', form)
      .then(response => {
        console.log(response.data);
        navigate('/');
      })
      .catch(error => {
        console.error('There was a problem with the request:', error);
        const popupError = () => {
          setEstActive(true);
        };
        popupError();
      });

  }



  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
      <Card className="w-full max-w-md">
        <CardHeader>
          <Link to="/" className="text-xl font-black tracking-tight">
            Ma<span className="text-primary">Part</span>
          </Link>
          <CardTitle className="mt-2 text-2xl">Créer un compte</CardTitle>
          <CardDescription>Renseignez vos informations pour vous inscrire.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="prenom">Prénom</Label>
                <Input id="prenom" required value={form.prenom} onChange={update('prenom')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="nom">Nom</Label>
                <Input id="nom" required value={form.nom} onChange={update('nom')} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="mail">Email</Label>
              <Input
                id="mail"
                type="email"
                required
                autoComplete="email"
                value={form.mail}
                onChange={update('mail')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="motDePasse">Mot de passe</Label>
              <Input
                id="motDePasse"
                type="password"
                required
                minLength={6}
                autoComplete="new-password"
                value={form.motDePasse}
                onChange={update('motDePasse')}
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                className="size-4 accent-primary"
                checked={form.estVendeur}
                onChange={update('estVendeur')}
              />
              Je suis dirigeant / vendeur de parts
            </label>
            <Button type="submit" className="w-full">
              Créer mon compte
            </Button>
            {estActive && (
              <Alert>
                <CircleXIcon />
                <AlertTitle>Adresse email déjà utilisée</AlertTitle>
                <AlertDescription>
                  Une compte existe déjà avec cette adresse email.
                </AlertDescription>
              </Alert>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
