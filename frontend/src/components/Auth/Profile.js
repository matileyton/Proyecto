import React, { useContext, useState, useEffect } from 'react';
import { Container, TextField, Button, Typography, Box, CircularProgress } from '@mui/material';
import { AuthContext } from '../../context/AuthContext';
import api from '../../api/api';
import { useSnackbar } from 'notistack';

function Profile() {
  // const { user } = useContext(AuthContext); // Eliminado si no se usa
  const { enqueueSnackbar } = useSnackbar();
  const [profileData, setProfileData] = useState({
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    telefono: '',
    direccion: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('users/profile/');
        setProfileData(response.data);
      } catch (error) {
        console.error('Error al obtener el perfil', error);
        enqueueSnackbar('Error al obtener el perfil', { variant: 'error' });
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [enqueueSnackbar]);

  const onChange = (e) => {
    setProfileData({ ...profileData, [e.target.name]: e.target.value });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put('users/profile/', profileData);
      enqueueSnackbar('Perfil actualizado exitosamente', { variant: 'success' });
    } catch (error) {
      console.error('Error al actualizar el perfil', error);
      const message =
        error.response && error.response.data
          ? Object.values(error.response.data).join(' ')
          : 'Error al actualizar el perfil';
      enqueueSnackbar(message, { variant: 'error' });
    }
  };

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ mt: 5, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 5 }}>
        <Typography variant="h4" gutterBottom>
          Mi Perfil
        </Typography>
        <form onSubmit={handleUpdate}>
          <TextField
            label="Usuario"
            name="username"
            value={profileData.username}
            onChange={onChange}
            fullWidth
            margin="normal"
            disabled
          />
          <TextField
            label="Nombre"
            name="first_name"
            value={profileData.first_name}
            onChange={onChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Apellido"
            name="last_name"
            value={profileData.last_name}
            onChange={onChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Correo Electrónico"
            name="email"
            type="email"
            value={profileData.email}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Teléfono"
            name="telefono"
            value={profileData.telefono}
            onChange={onChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Dirección"
            name="direccion"
            value={profileData.direccion}
            onChange={onChange}
            fullWidth
            margin="normal"
          />
          <Button variant="contained" color="primary" type="submit" fullWidth sx={{ mt: 2 }}>
            Actualizar Perfil
          </Button>
        </form>
      </Box>
    </Container>
  );
}

export default Profile;