import React, { useState, useContext } from 'react';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { AuthContext } from '../../context/AuthContext';
import { Link } from 'react-router-dom';
import { useSnackbar } from 'notistack';

function Register() {
  const { registerUser } = useContext(AuthContext);
  // const navigate = useNavigate(); // Eliminado si no se usa
  const { enqueueSnackbar } = useSnackbar();

  const [formData, setFormData] = useState({
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    telefono: '',
    direccion: '',
    password: '',
    password2: '',
  });

  const { username, first_name, last_name, email, telefono, direccion, password, password2 } = formData;

  const onChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== password2) {
      enqueueSnackbar('Las contraseñas no coinciden', { variant: 'warning' });
      return;
    }
    try {
      await registerUser({ username, first_name, last_name, email, telefono, direccion, password, password2 });
      // Redireccionamiento se maneja en AuthContext
    } catch (error) {
      // Manejo de errores en AuthContext
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 5 }}>
        <Typography variant="h4" gutterBottom>
          Registrarse
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
            label="Nombre"
            name="first_name"
            value={first_name}
            onChange={onChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Apellido"
            name="last_name"
            value={last_name}
            onChange={onChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Correo Electrónico"
            name="email"
            type="email"
            value={email}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Teléfono"
            name="telefono"
            value={telefono}
            onChange={onChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Dirección"
            name="direccion"
            value={direccion}
            onChange={onChange}
            fullWidth
            margin="normal"
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
          <TextField
            label="Confirmar Contraseña"
            name="password2"
            type="password"
            value={password2}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <Button variant="contained" color="primary" type="submit" fullWidth sx={{ mt: 2 }}>
            Registrarse
          </Button>
        </form>
        <Typography variant="body2" sx={{ mt: 2 }}>
          ¿Ya tienes una cuenta? <Link to="/login">Inicia Sesión</Link>
        </Typography>
      </Box>
    </Container>
  );
}

export default Register;