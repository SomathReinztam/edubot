import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);

  return (
    <nav className="bg-blue-600 p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white text-2xl font-bold">EduBot</Link>
        <div>
          {user ? (
            <div className="flex items-center space-x-4">
              <span className="text-white">Hola, {user.name || user.email}</span>
              <button 
                onClick={logout}
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
              >
                Cerrar Sesión
              </button>
            </div>
          ) : (
            <div className="space-x-4">
              <Link to="/login" className="text-white hover:text-blue-200">Iniciar Sesión</Link>
              <Link to="/register" className="text-white hover:text-blue-200">Registrarse</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
