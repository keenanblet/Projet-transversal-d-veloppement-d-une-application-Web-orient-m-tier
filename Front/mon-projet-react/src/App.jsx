import { Routes, Route } from 'react-router-dom'
import Home from '@/pages/Home'
import Inscription from '@/pages/Inscription'
import Connexion from '@/pages/Connexion'
import Societes from '@/pages/Societes'
import RedirectIfAuth from '@/components/ui/RedirectIfAuth'

function App() {
  return (
    <Routes>
      <Route path="/" element={<RedirectIfAuth><Home /></RedirectIfAuth>} />
      <Route path="/inscription" element={<RedirectIfAuth><Inscription /></RedirectIfAuth>} />
      <Route path="/connexion" element={<RedirectIfAuth><Connexion /></RedirectIfAuth>} />
      <Route path="/societes" element={<Societes />} />
    </Routes>
  )
}

export default App
