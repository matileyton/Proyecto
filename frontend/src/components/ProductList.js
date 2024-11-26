import React, { useEffect, useState } from 'react';
import api from '../api/api';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  CircularProgress,
  Box,
} from '@mui/material';
import { Link } from 'react-router-dom';
import { useSnackbar } from 'notistack';

function ProductList() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const { enqueueSnackbar } = useSnackbar();

  const fetchProducts = async () => {
    try {
      const response = await api.get('productos/');
      
      // Verificar si 'results' existe y es un array
      if (response.data && Array.isArray(response.data.results)) {
        setProducts(response.data.results);
      } else {
        console.warn('La respuesta de la API no contiene un array "results".');
        enqueueSnackbar('Estructura de respuesta desconocida al obtener productos.', { variant: 'warning' });
        setProducts([]); // Asignar un array vacío para evitar errores
      }
    } catch (error) {
      console.error('Error al obtener los productos', error);
      enqueueSnackbar('Error al obtener los productos.', { variant: 'error' });
      setProducts([]); // Asignar un array vacío en caso de error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // Asegurarse de que 'products' es un array antes de llamar a .filter()
  const filteredProducts = Array.isArray(products)
    ? products.filter(
        (product) =>
          product.nombre.toLowerCase().includes(search.toLowerCase()) ||
          product.descripcion.toLowerCase().includes(search.toLowerCase()) ||
          product.marca.toLowerCase().includes(search.toLowerCase())
      )
    : [];

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 5, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 5 }}>
      <Typography variant="h4" gutterBottom>
        Productos
      </Typography>
      <TextField
        label="Buscar Productos"
        variant="outlined"
        fullWidth
        margin="normal"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {filteredProducts.length === 0 ? (
        <Typography variant="h6">No se encontraron productos.</Typography>
      ) : (
        <Grid container spacing={4}>
          {filteredProducts.map((product) => (
            <Grid item key={product.id} xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                {/* Si tienes imágenes de productos, puedes descomentar y ajustar 'CardMedia' */}
                {/* <CardMedia
                  component="img"
                  image={product.imagen_url} // Asegúrate de que 'imagen_url' es la propiedad correcta
                  alt={product.nombre}
                  height="140"
                /> */}
                <CardContent>
                  <Typography gutterBottom variant="h5" component="div">
                    {product.nombre}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {product.descripcion.substring(0, 100)}...
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 2 }}>
                    ${product.precio_usd} USD
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" component={Link} to={`/products/${product.id}`}>
                    Ver Detalles
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}

export default ProductList;
