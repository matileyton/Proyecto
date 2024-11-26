import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { useSnackbar } from 'notistack';

function PrivateRoute({ children }) {
  const { user } = useContext(AuthContext);
  const { enqueueSnackbar } = useSnackbar();

  if (!user) {
    enqueueSnackbar('Debes iniciar sesión para acceder a esta página', { variant: 'warning' });
    return <Navigate to="/login" />;
  }

  return children;
}

export default PrivateRoute;
