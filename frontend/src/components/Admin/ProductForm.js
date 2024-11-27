import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import api from '../../api/api';
import { useSnackbar } from 'notistack';

function ProductForm() {
  const { id } = useParams(); // Si existe, es edición; si no, es creación
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [productData, setProductData] = useState({
    nombre: '',
    descripcion: '',
    marca: '',
    precio_usd: '',
    precio_final_clp: '',
    peso_kg: '',
    disponible: true,
  });

  useEffect(() => {
    if (id) {
      // Obtener datos del producto para editar
      const fetchProduct = async () => {
        try {
          const response = await api.get(`productos/${id}/`);
          setProductData(response.data);
        } catch (error) {
          console.error('Error al obtener el producto', error);
          enqueueSnackbar('Error al obtener el producto', { variant: 'error' });
        }
      };
      fetchProduct();
    }
  }, [id, enqueueSnackbar]);

  const onChange = (e) => {
    const { name, value } = e.target;
    setProductData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const onCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setProductData((prevData) => ({
      ...prevData,
      [name]: checked,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!productData.precio_usd && !productData.precio_final_clp) {
      enqueueSnackbar('Debes ingresar el precio en USD o el precio final en CLP.', { variant: 'warning' });
      return;
    }
    // Prepara los datos para enviar
    const dataToSend = {
      ...productData,
      precio_usd: productData.precio_usd || null,
      precio_final_clp: productData.precio_final_clp || null,
      peso_kg: productData.peso_kg || null,
    };

    try {
      if (id) {
        await api.put(`productos/${id}/`, dataToSend);
        enqueueSnackbar('Producto actualizado exitosamente', { variant: 'success' });
      } else {
        await api.post('productos/', dataToSend);
        enqueueSnackbar('Producto creado exitosamente', { variant: 'success' });
      }
      navigate('/admin/products');
    } catch (error) {
      console.error('Error al guardar el producto', error);
      const message =
        error.response && error.response.data
          ? Object.values(error.response.data).join(' ')
          : 'Error al guardar el producto';
      enqueueSnackbar(message, { variant: 'error' });
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 5 }}>
        <Typography variant="h4" gutterBottom>
          {id ? 'Editar Producto' : 'Agregar Producto'}
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Nombre"
            name="nombre"
            value={productData.nombre}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Descripción"
            name="descripcion"
            value={productData.descripcion}
            onChange={onChange}
            fullWidth
            margin="normal"
            multiline
            rows={4}
          />
          <TextField
            label="Marca"
            name="marca"
            value={productData.marca}
            onChange={onChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Precio USD"
            name="precio_usd"
            value={productData.precio_usd}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
          />
          <TextField
            label="Precio Final CLP"
            name="precio_final_clp"
            value={productData.precio_final_clp}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
          />
          <Typography variant="body2" color="textSecondary">
            Ingresa el precio en USD o el precio final en CLP. Si ingresas ambos, se usará el precio final en CLP.
          </Typography>
          <TextField
            label="Peso (kg)"
            name="peso_kg"
            value={productData.peso_kg}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={productData.disponible}
                onChange={onCheckboxChange}
                name="disponible"
              />
            }
            label="Disponible"
          />
          <Button variant="contained" color="primary" type="submit" fullWidth sx={{ mt: 2 }}>
            {id ? 'Actualizar Producto' : 'Crear Producto'}
          </Button>
        </form>
      </Box>
    </Container>
  );
}

export default ProductForm;