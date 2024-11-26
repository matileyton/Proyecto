import React, { useState } from 'react'; // Eliminado useContext
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import api from '../../api/api';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

function ChangePassword() {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [formData, setFormData] = useState({
    old_password: '',
    new_password: '',
    new_password2: '',
  });

  const { old_password, new_password, new_password2 } = formData;

  const onChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (new_password !== new_password2) {
      enqueueSnackbar('Las nuevas contraseñas no coinciden', { variant: 'warning' });
      return;
    }
    try {
      const response = await api.post('users/change-password/', {
        old_password,
        new_password,
      });
      enqueueSnackbar(response.data.message, { variant: 'success' });
      navigate('/profile');
    } catch (error) {
      console.error('Error al cambiar la contraseña', error);
      const message =
        error.response && error.response.data
          ? Object.values(error.response.data).join(' ')
          : 'Error al cambiar la contraseña';
      enqueueSnackbar(message, { variant: 'error' });
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 5 }}>
        <Typography variant="h4" gutterBottom>
          Cambiar Contraseña
        </Typography>
        <form onSubmit={handleChangePassword}>
          <TextField
            label="Contraseña Actual"
            name="old_password"
            type="password"
            value={old_password}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Nueva Contraseña"
            name="new_password"
            type="password"
            value={new_password}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Confirmar Nueva Contraseña"
            name="new_password2"
            type="password"
            value={new_password2}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <Button variant="contained" color="primary" type="submit" fullWidth sx={{ mt: 2 }}>
            Cambiar Contraseña
          </Button>
        </form>
      </Box>
    </Container>
  );
}

export default ChangePassword;