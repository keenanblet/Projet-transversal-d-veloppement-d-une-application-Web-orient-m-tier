import { Navigate } from 'react-router-dom'
import { useAuth } from '@/context/useAuth'

// inverse de RequireAuth : si l'utilisateur est déjà connecté, on l'envoie ailleurs
export default function RedirectIfAuth({ children, to = '/societes' }) {
  const { user, chargement } = useAuth()
  if (chargement) return null
  if (user) return <Navigate to={to} replace />
  return children
}
