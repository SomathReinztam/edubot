import { createContext, useContext, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import NewAnalysis from './pages/NewAnalysis.jsx'
import ViewAnalysis from './pages/ViewAnalysis.jsx'

export const UserContext = createContext(null)

export function useUser() {
  return useContext(UserContext)
}

function PrivateRoute({ children }) {
  const { user } = useUser()
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('edubot_user')) || null
    } catch {
      return null
    }
  })

  function login(userData) {
    setUser(userData)
    localStorage.setItem('edubot_user', JSON.stringify(userData))
  }

  function logout() {
    setUser(null)
    localStorage.removeItem('edubot_user')
  }

  return (
    <UserContext.Provider value={{ user, login, logout }}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/analysis/new" element={<PrivateRoute><NewAnalysis /></PrivateRoute>} />
          <Route path="/analysis/:id" element={<PrivateRoute><ViewAnalysis /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </UserContext.Provider>
  )
}
