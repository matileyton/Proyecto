import React, { useEffect, useState } from 'react';
import api from '../../api/api';
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
} from '@mui/material';
import { Link } from 'react-router-dom';
import { useSnackbar } from 'notistack';

function ProductListAdmin() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const { enqueueSnackbar } = useSnackbar();

  const fetchProducts = async () => {
    try {
      const response = await api.get('productos/');
      const data = response.data;

      const productsData = data.results ? data.results : data;
      setProducts(productsData);
    } catch (error) {
      console.error('Error al obtener los productos', error);
      enqueueSnackbar('Error al obtener los productos', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleDelete = async (id) => {
    try {
      await api.delete(`productos/${id}/`);
      enqueueSnackbar('Producto eliminado exitosamente', { variant: 'success' });
      setProducts((prevProducts) => prevProducts.filter((product) => product.id !== id));
    } catch (error) {
      console.error('Error al eliminar el producto', error);
      enqueueSnackbar('Error al eliminar el producto', { variant: 'error' });
    }
  };

  const filteredProducts = products.filter(
    (product) =>
      product.nombre.toLowerCase().includes(search.toLowerCase()) ||
      product.descripcion.toLowerCase().includes(search.toLowerCase()) ||
      product.marca.toLowerCase().includes(search.toLowerCase())
  );

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
        Gestionar Productos
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
                  <Button size="small" component={Link} to={`/admin/products/edit/${product.id}`}>
                    Editar
                  </Button>
                  <Button size="small" color="error" onClick={() => handleDelete(product.id)}>
                    Eliminar
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

export default ProductListAdmin;
