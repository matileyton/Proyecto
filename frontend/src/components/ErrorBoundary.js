import React from 'react';
import { Typography, Container, Button } from '@mui/material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Actualizar el estado para renderizar una interfaz de reserva
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Puedes registrar el error en un servicio de reporte de errores
    console.error('ErrorBoundary capturó un error:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Puedes personalizar la interfaz de error aquí
      return (
        <Container maxWidth="sm" sx={{ mt: 10, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            Algo salió mal.
          </Typography>
          <Typography variant="body1" gutterBottom>
            Por favor, intenta recargar la página.
          </Typography>
          <Button variant="contained" color="primary" onClick={this.handleReload}>
            Recargar
          </Button>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
