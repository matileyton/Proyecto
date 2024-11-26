import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';

function App() {
  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom>
          Bienvenido a Personal Shopper
        </Typography>
        <Typography variant="h6" gutterBottom>
          Tu solución personal para compras en línea
        </Typography>
        <Button variant="contained" color="primary" component={Link} to="/products" sx={{ mt: 3 }}>
          Ver Productos
        </Button>
      </Box>
    </Container>
  );
}

export default App;
