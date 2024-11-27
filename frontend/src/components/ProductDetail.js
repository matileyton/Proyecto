import React, { useEffect, useState, useContext } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api/api';
import {
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import { CartContext } from '../context/CartContext';
import { useSnackbar } from 'notistack';

function ProductDetail() {
  const { id } = useParams();
  const { addToCart } = useContext(CartContext);
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await api.get(`productos/${id}/`);
        setProduct(response.data);
      } catch (error) {
        console.error('Error al obtener el producto', error);
        enqueueSnackbar('Error al obtener el producto', { variant: 'error' });
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [id, enqueueSnackbar]);

  const handleAddToCart = () => {
    addToCart(product);
    enqueueSnackbar('Producto añadido al carrito', { variant: 'success' });
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 5, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!product) {
    return (
      <Container maxWidth="md" sx={{ mt: 5 }}>
        <Typography variant="h5">Producto no encontrado</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            {product.nombre}
          </Typography>
          <Typography variant="h6" gutterBottom>
            Marca: {product.marca}
          </Typography>
          <Typography variant="body1" gutterBottom>
            {product.descripcion}
          </Typography>
          <Typography variant="h5" color="primary" gutterBottom>
            Precio: ${product.precio_usd} USD
          </Typography>
          <Typography variant="body2" gutterBottom>
            Peso: {product.peso_kg} kg
          </Typography>
          <Typography variant="body2" gutterBottom>
            Disponible: {product.disponible ? 'Sí' : 'No'}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleAddToCart}
            disabled={!product.disponible}
            sx={{ mt: 2 }}
          >
            Añadir al Carrito
          </Button>
        </CardContent>
      </Card>
    </Container>
  );
}

export default ProductDetail;
