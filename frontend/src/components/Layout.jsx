import { Link, useNavigate } from 'react-router-dom'
import { useUser } from '../App.jsx'

export default function Layout({ children, wide }) {
  const { user, logout } = useUser()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <>
      <nav className="navbar">
        <Link to="/dashboard" className="navbar-brand">EduBot</Link>
        {user && (
          <div className="navbar-right">
            <span className="navbar-user">{user.name}</span>
            <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>
        )}
      </nav>
      <main className={wide ? 'page-wide' : 'page'}>
        {children}
      </main>
    </>
  )
}
