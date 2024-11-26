import React, { useContext, useState } from 'react';
import { Container, Typography, Button, Box, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material';
import { AuthContext } from '../../context/AuthContext';
import api from '../../api/api';
import { useSnackbar } from 'notistack';

function DeleteAccount() {
  const { logoutUser } = useContext(AuthContext);
  const { enqueueSnackbar } = useSnackbar();
  const [open, setOpen] = useState(false);

  const handleDelete = async () => {
    try {
      await api.delete('users/delete/');
      enqueueSnackbar('Cuenta eliminada exitosamente', { variant: 'success' });
      logoutUser();
    } catch (error) {
      console.error('Error al eliminar la cuenta', error);
      const message =
        error.response && error.response.data
          ? Object.values(error.response.data).join(' ')
          : 'Error al eliminar la cuenta';
      enqueueSnackbar(message, { variant: 'error' });
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 5, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
          Eliminar Cuenta
        </Typography>
        <Typography variant="body1" gutterBottom>
          Al eliminar tu cuenta, se borrarán todos tus datos de forma permanente.
        </Typography>
        <Button variant="contained" color="error" onClick={() => setOpen(true)}>
          Eliminar Cuenta
        </Button>

        <Dialog
          open={open}
          onClose={() => setOpen(false)}
        >
          <DialogTitle>Confirmar Eliminación</DialogTitle>
          <DialogContent>
            <DialogContentText>
              ¿Estás seguro de que deseas eliminar tu cuenta? Esta acción no se puede deshacer.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancelar</Button>
            <Button onClick={handleDelete} color="error">
              Eliminar
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}

export default DeleteAccount;
