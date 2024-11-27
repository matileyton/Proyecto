import React, { useState, useEffect } from 'react';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
} from '@mui/material';
import api from '../../api/api';
import { useSnackbar } from 'notistack';

function ConfiguracionForm() {
  const { enqueueSnackbar } = useSnackbar();
  const [configData, setConfigData] = useState({
    porcentaje_comision: '',
    tasa_seguro: '',
    costo_por_kg: '',
    tasa_arancel: '',
    tasa_iva: '',
  });

  useEffect(() => {
    // Obtener la configuración existente
    const fetchConfig = async () => {
      try {
        const response = await api.get('configuracion/');
        if (response.data && response.data.results && response.data.results.length > 0) {
          setConfigData(response.data.results[0]);
        } else {
          enqueueSnackbar('No se encontró configuración existente', { variant: 'warning' });
        }
      } catch (error) {
        console.error('Error al obtener la configuración', error);
        enqueueSnackbar('Error al obtener la configuración', { variant: 'error' });
      }
    };
    fetchConfig();
  }, [enqueueSnackbar]);

  const onChange = (e) => {
    const { name, value } = e.target;
    setConfigData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (configData.id) {
        // Actualizar configuración existente
        await api.put(`configuracion/${configData.id}/`, configData);
        enqueueSnackbar('Configuración actualizada exitosamente', { variant: 'success' });
      } else {
        // Crear nueva configuración
        await api.post('configuracion/', configData);
        enqueueSnackbar('Configuración creada exitosamente', { variant: 'success' });
      }
    } catch (error) {
      console.error('Error al guardar la configuración', error);
      const message =
        error.response && error.response.data
          ? Object.values(error.response.data).join(' ')
          : 'Error al guardar la configuración';
      enqueueSnackbar(message, { variant: 'error' });
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 5 }}>
        <Typography variant="h4" gutterBottom>
          Configurar Comisión y Tasas
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Porcentaje de Comisión"
            name="porcentaje_comision"
            value={configData.porcentaje_comision}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
            required
          />
          {/* Agrega otros campos según sea necesario */}
          <TextField
            label="Tasa de Seguro"
            name="tasa_seguro"
            value={configData.tasa_seguro}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
            required
          />
          <TextField
            label="Costo por kg"
            name="costo_por_kg"
            value={configData.costo_por_kg}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
            required
          />
          <TextField
            label="Tasa de Arancel"
            name="tasa_arancel"
            value={configData.tasa_arancel}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
            required
          />
          <TextField
            label="Tasa de IVA"
            name="tasa_iva"
            value={configData.tasa_iva}
            onChange={onChange}
            fullWidth
            margin="normal"
            type="number"
            inputProps={{ step: '0.01' }}
            required
          />
          <Button variant="contained" color="primary" type="submit" fullWidth sx={{ mt: 2 }}>
            Guardar Configuración
          </Button>
        </form>
      </Box>
    </Container>
  );
}

export default ConfiguracionForm;