import React from 'react';
import { Container, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';

function AdminDashboard() {
  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Typography variant="h4" gutterBottom>
        Panel de Administrador
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Button variant="contained" component={Link} to="/admin/products/new">
          Agregar Producto
        </Button>
        <Button variant="contained" component={Link} to="/admin/products">
          Gestionar Productos
        </Button>
        <Button variant="contained" component={Link} to="/admin/configuracion">
          Configurar Comisión
        </Button>
      </Box>
    </Container>
  );
}

export default AdminDashboard;
