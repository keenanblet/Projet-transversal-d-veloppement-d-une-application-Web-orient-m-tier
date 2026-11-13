import { Routes, Route } from 'react-router-dom'
import Home from '@/pages/Home'
import Inscription from '@/pages/Inscription'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/inscription" element={<Inscription />} />
    </Routes>
  )
}

export default App
