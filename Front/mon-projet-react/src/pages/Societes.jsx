import { useEffect, useState } from 'react'
import axios from 'axios'

const API = 'http://127.0.0.1:8000'

export default function Societes() {
  const [entreprises, setEntreprises] = useState([])
  // null si personne n'est connecté (à adapter à la façon dont ta page de connexion stocke l'utilisateur)
  const user = JSON.parse(localStorage.getItem('user'))

  useEffect(() => {
    axios
      .get(`${API}/v1/entreprises`)
      .then((res) => setEntreprises(res.data))
      .catch((err) => console.error(err))
  }, [])

  function acheter(siret) {
    axios
      .post(
        `${API}/v1/entreprises/${siret}/achats`,
        { quantite: 1 },
        { headers: { 'X-User-Id': user.id } }
      )
      .then(() => alert('Achat effectué'))
      .catch(() => alert('Achat impossible'))
  }

  return (
    <div>
      <h1>Sociétés</h1>
      <table>
        <thead>
          <tr>
            <th>Nom</th>
            <th>SIRET</th>
            <th>Prix d'une part</th>
            {user && <th></th>}
          </tr>
        </thead>
        <tbody>
          {entreprises.map((e) => (
            <tr key={e.siret}>
              <td>{e.nom}</td>
              <td>{e.siret}</td>
              <td>{e.prixPart} €</td>
              {user && (
                <td>
                  <button onClick={() => acheter(e.siret)}>Acheter</button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
