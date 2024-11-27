import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import App from './App';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import ProductList from './components/ProductList';
import ProductDetail from './components/ProductDetail';
import Cart from './components/Cart';
import OrderHistory from './components/OrderHistory';
import Profile from './components/Auth/Profile';
import ChangePassword from './components/Auth/ChangePassword';
import PrivateRoute from './components/PrivateRoute';
import DeleteAccount from './components/Auth/DeleteAccount';
import AdminRoute from './components/AdminRoute';
import ProductListAdmin from './components/Admin/ProductListAdmin';
import AdminDashboard from './components/Admin/AdminDashboard';
import ProductForm from './components/Admin/ProductForm';
import ConfiguracionForm from './components/Admin/ConfiguracionForm';

function AppRoutes() {
  return (
    <AuthProvider>
      <CartProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/products" element={<ProductList />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route
            path="/orders"
            element={
              <PrivateRoute>
                <OrderHistory />
              </PrivateRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <Profile />
              </PrivateRoute>
            }
          />
          <Route
            path="/change-password"
            element={
              <PrivateRoute>
                <ChangePassword />
              </PrivateRoute>
            }
          />
          <Route
            path="/delete-account"
            element={
              <PrivateRoute>
                <DeleteAccount />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/products/new"
            element={
              <AdminRoute>
                <ProductForm />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/products/edit/:id"
            element={
              <AdminRoute>
                <ProductForm />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/configuracion"
            element={
              <AdminRoute>
                <ConfiguracionForm />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/products"
            element={
              <AdminRoute>
                <ProductListAdmin />
              </AdminRoute>
            }
          />
        </Routes>
      </CartProvider>
    </AuthProvider>
  );
}

export default AppRoutes;
