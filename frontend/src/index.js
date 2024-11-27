import React from 'react';
import ReactDOM from 'react-dom/client'; 
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './Routes';
import reportWebVitals from './reportWebVitals';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';
import ErrorBoundary from './components/ErrorBoundary'; 

const root = ReactDOM.createRoot(document.getElementById('root')); 

root.render(
  <React.StrictMode>
    <CssBaseline />
    <BrowserRouter
      future={{ v7_startTransition: true }}
    >
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <ErrorBoundary>
          <AppRoutes />
        </ErrorBoundary>
      </SnackbarProvider>
    </BrowserRouter>
  </React.StrictMode>
);

reportWebVitals();
