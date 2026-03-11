import { useState } from 'react'
import AuthForm from './components/AuthForm'
import Dashboard from './components/Dashboard'

export default function App() {
  const [user, setUser] = useState(() => {
    const saved = sessionStorage.getItem('edubot_user')
    return saved ? JSON.parse(saved) : null
  })

  const handleLogin = (userData) => {
    sessionStorage.setItem('edubot_user', JSON.stringify(userData))
    setUser(userData)
  }

  const handleLogout = () => {
    sessionStorage.removeItem('edubot_user')
    setUser(null)
  }

  return user
    ? <Dashboard user={user} onLogout={handleLogout} />
    : <AuthForm onLogin={handleLogin} />
}
