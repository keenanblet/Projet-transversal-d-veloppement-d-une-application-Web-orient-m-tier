import { Navigate } from 'react-router-dom'
import { useAuth } from '@/context/useAuth'

export default function RequireAuth({ children }) {
  const { user, chargement } = useAuth()
  if (chargement) return null
  if (!user) return <Navigate to="/connexion" replace />
  return children
}
