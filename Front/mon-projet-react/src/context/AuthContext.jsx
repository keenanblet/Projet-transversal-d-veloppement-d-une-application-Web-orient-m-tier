import { createContext, useEffect, useState } from 'react'
import { api } from '@/lib/api'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [chargement, setChargement] = useState(true)

  // au démarrage de l'app : est-ce qu'un cookie valide existe déjà ?
  useEffect(() => {
    api.get('/v1/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => setUser(null))
      .finally(() => setChargement(false))
  }, [])

  async function login(mail, motDePasse) {
    const res = await api.post('/v1/auth/login', { mail, motDePasse })
    setUser(res.data) // le back renvoie le user, le cookie est posé tout seul
  }

  async function logout() {
    await api.post('/v1/auth/logout')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, chargement, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
