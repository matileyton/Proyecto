import React, { useEffect, useState } from 'react';
import api from '../api/api';
import {
  Container,
  Typography,
  List,
  ListItem,
  ListItemText,
  Collapse,
  ListItemButton,
  CircularProgress,
} from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { useSnackbar } from 'notistack';

function OrderHistory() {
  const [orders, setOrders] = useState([]);
  const [openOrderIds, setOpenOrderIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await api.get('pedidos/');

        // Verificar si 'results' existe y es un array (paginación)
        if (response.data && Array.isArray(response.data.results)) {
          setOrders(response.data.results);
        } else if (Array.isArray(response.data)) {
          // Si no hay paginación, usar directamente el array
          setOrders(response.data);
        } else {
          console.warn('La respuesta de la API no contiene un array "results" ni es un array directo.');
          enqueueSnackbar('Estructura de respuesta desconocida al obtener pedidos.', { variant: 'warning' });
          setOrders([]); // Asignar un array vacío para evitar errores
        }
      } catch (error) {
        console.error('Error al obtener los pedidos', error);
        enqueueSnackbar('Error al obtener los pedidos.', { variant: 'error' });
        setOrders([]); // Asignar un array vacío en caso de error
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, [enqueueSnackbar]);

  const handleToggle = (orderId) => {
    setOpenOrderIds((prevOpen) =>
      prevOpen.includes(orderId)
        ? prevOpen.filter((id) => id !== orderId)
        : [...prevOpen, orderId]
    );
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 5, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Typography variant="h4" gutterBottom>
        Historial de Pedidos
      </Typography>
      {orders.length === 0 ? (
        <Typography variant="h6">No hay pedidos realizados</Typography>
      ) : (
        <List>
          {orders.map((order) => (
            <React.Fragment key={order.id}>
              <ListItemButton onClick={() => handleToggle(order.id)}>
                <ListItemText
                  primary={`Pedido #${order.id}`}
                  secondary={`Total: ${order.total_final_clp} CLP - Fecha: ${new Date(order.fecha_pedido).toLocaleString()}`}
                />
                {openOrderIds.includes(order.id) ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>
              <Collapse in={openOrderIds.includes(order.id)} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  {order.detalles && order.detalles.length > 0 ? (
                    order.detalles.map((detalle) => (
                      <ListItem key={detalle.id} sx={{ pl: 4 }}>
                        <ListItemText
                          primary={detalle.producto.nombre}
                          secondary={`Cantidad: ${detalle.cantidad} - Subtotal: ${detalle.subtotal_clp} CLP`}
                        />
                      </ListItem>
                    ))
                  ) : (
                    <ListItem sx={{ pl: 4 }}>
                      <ListItemText primary="No hay detalles para este pedido." />
                    </ListItem>
                  )}
                </List>
              </Collapse>
            </React.Fragment>
          ))}
        </List>
      )}
    </Container>
  );
}

export default OrderHistory;
