import { Routes, Route } from 'react-router-dom'
import Home from '@/pages/Home'
import Inscription from '@/pages/Inscription'
import Connexion from '@/pages/Connexion'
import Societes from '@/pages/Societes'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/inscription" element={<Inscription />} />
      <Route path="/connexion" element={<Connexion />} />
      <Route path="/societes" element={<Societes />} />
    </Routes>
  )
}

export default App
