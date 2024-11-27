import React, { useState, useContext } from 'react';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { AuthContext } from '../../context/AuthContext';
import { Link } from 'react-router-dom';
import { useSnackbar } from 'notistack';

function Login() {
  const { loginUser } = useContext(AuthContext);
  useSnackbar();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const { username, password } = formData;

  const onChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await loginUser(username, password);
      // Las notificaciones se manejan en AuthContext
    } catch (error) {
      // Las notificaciones de error ya se manejan en AuthContext
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 5 }}>
        <Typography variant="h4" gutterBottom>
          Iniciar Sesión
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Usuario"
            name="username"
            value={username}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Contraseña"
            name="password"
            type="password"
            value={password}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <Button variant="contained" color="primary" type="submit" fullWidth sx={{ mt: 2 }}>
            Iniciar Sesión
          </Button>
        </form>
        <Typography variant="body2" sx={{ mt: 2 }}>
          ¿No tienes una cuenta? <Link to="/register">Regístrate aquí</Link>
        </Typography>
      </Box>
    </Container>
  );
}

export default Login;
