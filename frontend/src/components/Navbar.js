import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function Navbar() {
  const { user, logoutUser, isAdmin } = useContext(AuthContext);

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Personal Shopper
        </Typography>
        <Box>
          <Button color="inherit" component={Link} to="/">
            Inicio
          </Button>
          <Button color="inherit" component={Link} to="/products">
            Productos
          </Button>
          {user ? (
            <>
              <Button color="inherit" component={Link} to="/cart">
                Carrito
              </Button>
              <Button color="inherit" component={Link} to="/orders">
                Mis Pedidos
              </Button>
              <Button color="inherit" component={Link} to="/profile">
                Perfil
              </Button>
              <Button color="inherit" component={Link} to="/change-password">
                Cambiar Contraseña
              </Button>
              <Button color="inherit" component={Link} to="/delete-account">
                Eliminar Cuenta
              </Button>
              {isAdmin && (
                <>
                  <Button color="inherit" component={Link} to="/admin">
                    Administrador
                  </Button>
                </>
              )}
              <Button color="inherit" onClick={logoutUser}>
                Cerrar Sesión
              </Button>
            </>
          ) : (
            <>
              <Button color="inherit" component={Link} to="/login">
                Iniciar Sesión
              </Button>
              <Button color="inherit" component={Link} to="/register">
                Registrarse
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
