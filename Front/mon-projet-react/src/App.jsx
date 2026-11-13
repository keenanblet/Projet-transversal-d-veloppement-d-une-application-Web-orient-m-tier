import { Routes, Route } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'

function Users() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => api('/v1/users'),
  })
  if (isLoading) return <p>Chargement...</p>
  if (error) return <p>Erreur : {error.message}</p>
  return (
    <ul className="list-disc pl-6">
      {data.map((u) => (
        <li key={u.id}>{JSON.stringify(u)}</li>
      ))}
    </ul>
  )
}

function App() {
  return (
    <div className="p-8 space-y-4">
      <h1 className="text-3xl font-bold">MaPart</h1>
      <Button>Bouton shadcn</Button>
      <Routes>
        <Route path="/" element={<Users />} />
      </Routes>
    </div>
  )
}

export default App
