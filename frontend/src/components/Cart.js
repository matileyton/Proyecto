import React, { useContext } from 'react';
import { CartContext } from '../context/CartContext';
import api from '../api/api';
import {
  Container,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Button,
  TextField,
  Box,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { useSnackbar } from 'notistack';
import { useNavigate } from 'react-router-dom';

function Cart() {
  const { cartItems, removeFromCart, updateQuantity, clearCart } = useContext(CartContext);
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();

  const handleCheckout = async () => {
    try {
      const detalles = cartItems.map((item) => ({
        producto: item.id,
        cantidad: item.quantity,
      }));
      await api.post('pedidos/', { detalles });
      enqueueSnackbar('Pedido realizado con éxito', { variant: 'success' });
      clearCart();
      navigate('/orders');
    } catch (error) {
      console.error('Error al realizar el pedido', error);
      enqueueSnackbar('Error al realizar el pedido', { variant: 'error' });
    }
  };

  const handleQuantityChange = (id, quantity) => {
    if (quantity < 1) return;
    updateQuantity(id, quantity);
  };

  const totalUSD = cartItems.reduce((sum, item) => sum + item.precio_usd * item.quantity, 0);
  const totalCLP = cartItems.reduce((sum, item) => sum + (item.precio_clp || 0) * item.quantity, 0);

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Typography variant="h4" gutterBottom>
        Carrito de Compras
      </Typography>
      {cartItems.length === 0 ? (
        <Typography variant="h6">El carrito está vacío</Typography>
      ) : (
        <>
          <List>
            {cartItems.map((item) => (
              <ListItem
                key={item.id}
                secondaryAction={
                  <IconButton edge="end" aria-label="delete" onClick={() => removeFromCart(item.id)}>
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemText
                  primary={item.nombre}
                  secondary={`Precio: ${item.precio_usd} USD`}
                />
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TextField
                    type="number"
                    value={item.quantity}
                    onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value))}
                    inputProps={{ min: 1, style: { width: '60px' } }}
                    size="small"
                  />
                </Box>
              </ListItem>
            ))}
          </List>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6">
              Total: {totalUSD.toFixed(2)} USD {totalCLP ? `/ ${totalCLP.toFixed(2)} CLP` : ''}
            </Typography>
            <Button variant="contained" color="primary" onClick={handleCheckout} sx={{ mt: 2 }}>
              Realizar Pedido
            </Button>
          </Box>
        </>
      )}
    </Container>
  );
}

export default Cart;
