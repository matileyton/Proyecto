import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { useSnackbar } from 'notistack';

function AdminRoute({ children }) {
  const { user, isAdmin } = useContext(AuthContext);
  const { enqueueSnackbar } = useSnackbar();

  if (!user || !isAdmin) {
    enqueueSnackbar('Acceso denegado. Se requiere permisos de administrador.', { variant: 'warning' });
    return <Navigate to="/" />;
  }

  return children;
}

export default AdminRoute;
