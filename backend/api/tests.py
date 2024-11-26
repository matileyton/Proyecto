# backend/api/tests.py

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from decimal import Decimal
from .models import Producto, Configuracion, Pedido, DetallePedido, Notificacion
from rest_framework_simplejwt.tokens import RefreshToken
from .tasks import tarea_actualizar_dolar_aduanero
from rest_framework.exceptions import PermissionDenied
import json
import requests

User = get_user_model()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ConfiguracionModelTest(TestCase):
    def setUp(self):
        self.configuracion = Configuracion.objects.create(
            porcentaje_comision=Decimal('15.0'),
            tasa_seguro=Decimal('1.0'),
            costo_por_kg=Decimal('5.0'),
            tasa_arancel=Decimal('6.0'),
            tasa_iva=Decimal('19.0'),
        )

    @patch('api.utils.obtener_dolar_aduanero')
    def test_actualizar_dolar_aduanero(self, mock_obtener_dolar):
        mock_obtener_dolar.return_value = Decimal('800.0')
        self.configuracion.actualizar_dolar_aduanero()
        self.configuracion.refresh_from_db()
        self.assertEqual(self.configuracion.dolar_aduanero, Decimal('800.0'))
        self.assertIsNotNone(self.configuracion.fecha_actualizacion_dolar_aduanero)


class ProductoModelTest(TestCase):
    @patch('api.utils.obtener_valor_dolar')
    def setUp(self, mock_obtener_valor_dolar):
        mock_obtener_valor_dolar.return_value = (Decimal('750.0'), '2024-11-21T00:00:00Z')
        self.configuracion = Configuracion.objects.create(
            porcentaje_comision=Decimal('15.0'),
            tasa_seguro=Decimal('1.0'),
            costo_por_kg=Decimal('5.0'),
            tasa_arancel=Decimal('6.0'),
            tasa_iva=Decimal('19.0'),
        )
        self.producto = Producto.objects.create(
            nombre="Producto Test",
            descripcion="Descripción del producto de prueba",
            marca="Marca Test",
            precio_usd=Decimal('100.0'),
            peso_kg=Decimal('2.0'),
            disponible=True
        )

    @patch('api.utils.obtener_valor_dolar')
    def test_precio_clp_property(self, mock_obtener_valor_dolar):
        mock_obtener_valor_dolar.return_value = (Decimal('750.0'), '2024-11-21T00:00:00Z')
        precio_clp = self.producto.precio_clp
        expected_price = (Decimal('100.0') + (Decimal('100.0') * Decimal('15.0') / Decimal('100.0'))) * Decimal('750.0')
        self.assertEqual(precio_clp, expected_price)

    def test_str_method(self):
        self.assertEqual(str(self.producto), "Producto Test - Marca Test")


class UsuarioModelTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="usuario_test",
            password="password123",
            email="test@example.com",
            telefono="123456789",
            direccion="Calle Falsa 123"
        )

    def test_creacion_usuario(self):
        self.assertEqual(self.usuario.username, "usuario_test")
        self.assertTrue(self.usuario.check_password("password123"))
        self.assertEqual(self.usuario.email, "test@example.com")
        self.assertEqual(self.usuario.telefono, "123456789")
        self.assertEqual(self.usuario.direccion, "Calle Falsa 123")

    def test_str_method(self):
        self.assertEqual(str(self.usuario), "usuario_test")


class PedidoModelTest(TestCase):
    @patch('api.utils.obtener_valor_dolar')
    def setUp(self, mock_obtener_valor_dolar):
        mock_obtener_valor_dolar.return_value = (Decimal('750.0'), '2024-11-21T00:00:00Z')
        self.usuario = User.objects.create_user(username="cliente", password="password123")
        self.producto = Producto.objects.create(
            nombre="Producto Prueba",
            descripcion="Descripción prueba",
            marca="Marca",
            precio_usd=Decimal('150.0'),
            peso_kg=Decimal('3.0'),
            disponible=True
        )
        self.pedido = Pedido.objects.create(
            cliente=self.usuario,
            total_usd=Decimal('150.0'),
            total_clp=Decimal('0'),
            peso_total_kg=Decimal('3.0')
        )

    @patch('api.utils.obtener_valor_dolar')
    def test_save_pedido_asigna_valor_dolar(self, mock_obtener_dolar):
        mock_obtener_dolar.return_value = (Decimal('750.0'), '2024-11-21T00:00:00Z')
        nuevo_pedido = Pedido.objects.create(
            cliente=self.usuario,
            total_usd=Decimal('200.0'),
            total_clp=Decimal('0'),
            peso_total_kg=Decimal('4.0')
        )
        self.assertEqual(nuevo_pedido.valor_dolar, Decimal('750.0'))

    def test_actualizar_totales(self):
        DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=2
        )
        self.pedido.actualizar_totales()
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.total_usd, Decimal('300.0'))
        self.assertEqual(self.pedido.peso_total_kg, Decimal('6.0'))

    @patch('api.utils.obtener_dolar_aduanero')
    def test_calcular_impuesto_aduanero(self, mock_obtener_dolar_aduanero):
        mock_obtener_dolar_aduanero.return_value = Decimal('750.0')
        DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=2
        )
        self.pedido.actualizar_totales()
        self.pedido.calcular_impuesto_aduanero()
        self.pedido.refresh_from_db()
        # Cálculos basados en Configuracion por defecto
        # total_usd = 300.0
        # seguro = 300.0 * 1 / 100 = 3.0
        # flete = 6.0 * 5 = 30.0
        # valor_cif_usd = 300.0 + 3.0 + 30.0 = 333.0
        # valor_cif_clp = 333.0 * 750.0 = 249750.0
        # arancel = 249750.0 * 6 / 100 = 14985.0
        # iva_importacion = (249750.0 + 14985.0) * 19 / 100 = 4994.55
        # total_impuestos = 14985.0 + 4994.55 = 19979.55
        # total_clp = 0 + 19979.55 = 19979.55
        self.assertAlmostEqual(self.pedido.total_final_clp, Decimal('19979.55'), places=2)


class DetallePedidoModelTest(TestCase):
    @patch('api.utils.obtener_valor_dolar')
    def setUp(self, mock_obtener_valor_dolar):
        mock_obtener_valor_dolar.return_value = (Decimal('700.0'), '2024-11-21T00:00:00Z')
        self.usuario = User.objects.create_user(username="cliente_detalle", password="password123")
        self.producto = Producto.objects.create(
            nombre="Producto Detalle",
            descripcion="Descripción detalle",
            marca="Marca Detalle",
            precio_usd=Decimal('50.0'),
            peso_kg=Decimal('1.5'),
            disponible=True
        )
        self.pedido = Pedido.objects.create(
            cliente=self.usuario,
            total_usd=Decimal('0'),
            total_clp=Decimal('0'),
            peso_total_kg=Decimal('0')
        )

    def test_save_detalle_pedido_calcula_subtotales(self):
        detalle = DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=3
        )
        detalle.save()
        self.assertEqual(detalle.subtotal_usd, Decimal('150.00'))
        self.assertEqual(detalle.peso_kg, Decimal('4.50'))

    @patch('api.utils.obtener_valor_dolar')
    def test_save_detalle_pedido_calcula_subtotal_clp(self, mock_obtener_dolar):
        mock_obtener_dolar.return_value = (Decimal('700.0'), '2024-11-21T00:00:00Z')
        detalle = DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=2
        )
        detalle.save()
        expected_subtotal_clp = (Decimal('50.0') + (Decimal('50.0') * Decimal('15.0') / Decimal('100.0'))) * Decimal('700.0') * Decimal('2')
        self.assertEqual(detalle.subtotal_clp, expected_subtotal_clp)


class NotificacionModelTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="cliente_notif", password="password123")
        self.notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo='estado_pedido',
            contenido='Su pedido ha sido recibido.',
        )

    def test_str_method(self):
        self.assertEqual(str(self.notificacion), f"Notificación para {self.usuario.username} - estado_pedido")

    def test_notificacion_default_leida(self):
        self.assertFalse(self.notificacion.leida)


class UserRegistrationSerializerTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user-register')
        self.user_data = {
            "username": "nuevo_usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "nuevo@example.com",
            "telefono": "987654321",
            "direccion": "Calle Nueva 456",
            "password": "SecurePass123",
            "password2": "SecurePass123"
        }

    def test_registro_usuario_exitosa(self):
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        usuario = User.objects.get(username="nuevo_usuario")
        self.assertEqual(usuario.email, "nuevo@example.com")
        self.assertTrue(usuario.check_password("SecurePass123"))

    def test_registro_contrasenas_no_coinciden(self):
        data = self.user_data.copy()
        data['password2'] = "DifferentPass123"
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class ProductoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="adminpass123",
            email="admin@example.com"
        )
        self.regular_user = User.objects.create_user(
            username="usuario_regular",
            password="userpass123",
            email="user@example.com"
        )
        self.producto_data = {
            "nombre": "Producto API",
            "descripcion": "Descripción del producto",
            "marca": "Marca API",
            "precio_usd": "100.00",
            "peso_kg": "2.00",
            "disponible": True
        }
        self.url = reverse('producto-list')

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_crear_producto_como_admin(self):
        token = self.obtener_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, self.producto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(Producto.objects.get().nombre, "Producto API")

    def test_crear_producto_como_usuario_regular_denegado(self):
        token = self.obtener_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, self.producto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Producto.objects.count(), 0)

    def test_obtener_lista_productos(self):
        Producto.objects.create(**self.producto_data)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_actualizar_producto_como_admin(self):
        producto = Producto.objects.create(**self.producto_data)
        url = reverse('producto-detail', args=[producto.id])
        updated_data = self.producto_data.copy()
        updated_data['nombre'] = "Producto Actualizado"
        token = self.obtener_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, "Producto Actualizado")

    def test_actualizar_producto_como_usuario_regular_denegado(self):
        producto = Producto.objects.create(**self.producto_data)
        url = reverse('producto-detail', args=[producto.id])
        updated_data = self.producto_data.copy()
        updated_data['nombre'] = "Producto Actualizado"
        token = self.obtener_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, "Producto API")


class PedidoAPITestCase(TestCase):
    @patch('api.utils.obtener_valor_dolar')
    def setUp(self, mock_obtener_valor_dolar):
        mock_obtener_valor_dolar.return_value = (Decimal('700.0'), '2024-11-21T00:00:00Z')
        self.client = APIClient()
        self.usuario = User.objects.create_user(username="cliente_pedido", password="password123")
        self.producto = Producto.objects.create(
            nombre="Producto Pedido",
            descripcion="Descripción Pedido",
            marca="Marca Pedido",
            precio_usd=Decimal('150.0'),
            peso_kg=Decimal('3.0'),
            disponible=True
        )
        self.url = reverse('pedido-list')
        self.pedido_data = {
            "detalles": [
                {
                    "producto": {
                        "id": self.producto.id
                    },
                    "cantidad": 2
                }
            ]
        }

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    @patch('api.utils.obtener_valor_dolar')
    def test_crear_pedido(self, mock_obtener_dolar):
        mock_obtener_dolar.return_value = (Decimal('700.0'), '2024-11-21T00:00:00Z')
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, self.pedido_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.cliente, self.usuario)
        self.assertEqual(pedido.total_usd, Decimal('300.0'))
        self.assertEqual(pedido.peso_total_kg, Decimal('6.0'))
        # Asumiendo Configuracion por defecto, total_clp debería ser calculado correctamente
        # Aquí debes ajustar el valor esperado según tu lógica de negocio
        # Por ejemplo:
        # total_clp = subtotal_usd * dolar_aduanero = 300 * 700 = 210000
        self.assertEqual(pedido.total_clp, Decimal('210000.00'))

    @patch('api.utils.obtener_valor_dolar')
    def test_obtener_pedidos_usuario(self, mock_obtener_dolar):
        mock_obtener_dolar.return_value = (Decimal('700.0'), '2024-11-21T00:00:00Z')
        Pedido.objects.create(
            cliente=self.usuario,
            total_usd=Decimal('150.0'),
            total_clp=Decimal('0'),
            peso_total_kg=Decimal('3.0')
        )
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_crear_pedido_sin_detalles_falla(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Pedido.objects.count(), 0)


class NotificacionAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(username="cliente_notif_api", password="password123")
        self.notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo='estado_pedido',
            contenido='Su pedido ha sido recibido.',
        )
        self.url = reverse('notificacion-list')

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_obtener_notificaciones_usuario(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_no_obtener_notificaciones_de_otro_usuario(self):
        otro_usuario = User.objects.create_user(username="otro_usuario", password="password456")
        Notificacion.objects.create(
            usuario=otro_usuario,
            tipo='promocion',
            contenido='Promoción exclusiva para ti.',
        )
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.url, format='json')
        self.assertEqual(len(response.data['results']), 1)  # Solo la notificación del usuario original


class UserProfileAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(
            username="perfil_usuario",
            password="password123",
            email="perfil@example.com",
            telefono="555555555",
            direccion="Calle Perfil 789"
        )
        self.url = reverse('user-profile')

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_obtener_perfil_usuario(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "perfil_usuario")
        self.assertEqual(response.data['email'], "perfil@example.com")
        self.assertEqual(response.data['telefono'], "555555555")
        self.assertEqual(response.data['direccion'], "Calle Perfil 789")

    def test_actualizar_perfil_usuario(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        update_data = {
            "first_name": "Nuevo Nombre",
            "last_name": "Nuevo Apellido",
            "telefono": "666666666",
            "direccion": "Nueva Calle 101"
        }
        response = self.client.patch(self.url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.first_name, "Nuevo Nombre")
        self.assertEqual(self.usuario.last_name, "Nuevo Apellido")
        self.assertEqual(self.usuario.telefono, "666666666")
        self.assertEqual(self.usuario.direccion, "Nueva Calle 101")


class ChangePasswordAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(username="cambiar_pass", password="oldPassword123")
        self.url = reverse('change-password')

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_cambiar_contrasena_exitosamente(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            "old_password": "oldPassword123",
            "new_password": "newSecurePass456"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password("newSecurePass456"))

    def test_cambiar_contrasena_con_old_password_incorrecto(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            "old_password": "wrongPassword",
            "new_password": "newSecurePass456"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_cambiar_contrasena_sin_old_password(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            "new_password": "newSecurePass456"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteAccountAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(username="eliminar_usuario", password="password123")
        self.url = reverse('delete-account')

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_eliminar_cuenta_exitosamente(self):
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username="eliminar_usuario").exists())

    def test_eliminar_cuenta_no_autenticado_falla(self):
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConfiguracionAPITestCase(TestCase):
    @patch('api.utils.obtener_dolar_aduanero')
    def setUp(self, mock_obtener_dolar_aduanero):
        mock_obtener_dolar_aduanero.return_value = Decimal('800.0')
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin_config",
            password="adminpass123",
            email="admin_config@example.com"
        )
        self.url = reverse('configuracion-list')
        self.config_data = {
            "porcentaje_comision": "20.0",
            "tasa_seguro": "2.0",
            "costo_por_kg": "10.0",
            "tasa_arancel": "8.0",
            "tasa_iva": "21.0",
            "dolar_aduanero": "800.0",
            "fecha_actualizacion_dolar_aduanero": "2024-12-01T00:00:00Z"
        }

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_crear_configuracion_como_admin(self):
        token = self.obtener_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, self.config_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Configuracion.objects.count(), 1)
        config = Configuracion.objects.get()
        self.assertEqual(config.porcentaje_comision, Decimal('20.0'))

    def test_crear_configuracion_como_usuario_regular_denegado(self):
        usuario_regular = User.objects.create_user(username="usuario_regular_config", password="userpass123")
        token = self.obtener_token(usuario_regular)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, self.config_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_obtener_lista_configuraciones_como_admin(self):
        Configuracion.objects.create(
            porcentaje_comision=Decimal('15.0'),
            tasa_seguro=Decimal('1.0'),
            costo_por_kg=Decimal('5.0'),
            tasa_arancel=Decimal('6.0'),
            tasa_iva=Decimal('19.0'),
        )
        token = self.obtener_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_actualizar_configuracion_como_admin(self):
        config = Configuracion.objects.create(
            porcentaje_comision=Decimal('15.0'),
            tasa_seguro=Decimal('1.0'),
            costo_por_kg=Decimal('5.0'),
            tasa_arancel=Decimal('6.0'),
            tasa_iva=Decimal('19.0'),
        )
        url = reverse('configuracion-detail', args=[config.id])
        updated_data = self.config_data.copy()
        updated_data['porcentaje_comision'] = "25.0"
        token = self.obtener_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        config.refresh_from_db()
        self.assertEqual(config.porcentaje_comision, Decimal('25.0'))


class DetallePedidoAPITestCase(TestCase):
    @patch('api.utils.obtener_valor_dolar')
    def setUp(self, mock_obtener_valor_dolar):
        mock_obtener_valor_dolar.return_value = (Decimal('700.0'), '2024-11-21T00:00:00Z')
        self.client = APIClient()
        self.usuario = User.objects.create_user(username="detalle_usuario", password="password123")
        self.producto = Producto.objects.create(
            nombre="Producto Detalle API",
            descripcion="Descripción Detalle API",
            marca="Marca Detalle API",
            precio_usd=Decimal('100.0'),
            peso_kg=Decimal('2.0'),
            disponible=True
        )
        self.pedido = Pedido.objects.create(
            cliente=self.usuario,
            total_usd=Decimal('100.0'),
            total_clp=Decimal('0'),
            peso_total_kg=Decimal('2.0')
        )
        self.url = reverse('detallepedido-list')
        self.detalle_data = {
            "pedido": self.pedido.id,
            "producto": self.producto.id,
            "cantidad": 3
        }

    def obtener_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    @patch('api.utils.obtener_valor_dolar')
    def test_crear_detalle_pedido(self, mock_obtener_dolar):
        mock_obtener_dolar.return_value = (Decimal('700.0'), '2024-11-21T00:00:00Z')
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, self.detalle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DetallePedido.objects.count(), 1)
        detalle = DetallePedido.objects.get()
        self.assertEqual(detalle.cantidad, 3)
        self.assertEqual(detalle.subtotal_usd, Decimal('300.00'))
        self.assertEqual(detalle.peso_kg, Decimal('6.00'))
        # Verificar que los totales del pedido se actualizan
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.total_usd, Decimal('300.00'))
        self.assertEqual(self.pedido.peso_total_kg, Decimal('8.00'))

    def test_crear_detalle_pedido_para_otro_usuario_denegado(self):
        otro_usuario = User.objects.create_user(username="otro_usuario_detalle", password="password456")
        self.pedido.cliente = otro_usuario
        self.pedido.save()
        token = self.obtener_token(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url, self.detalle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(DetallePedido.objects.count(), 0)


class TareaCeleryTestCase(TestCase):
    @patch('api.tasks.Configuracion.actualizar_dolar_aduanero')
    def test_tarea_actualizar_dolar_aduanero_llama_metodo_correcto(self, mock_actualizar):
        tarea_actualizar_dolar_aduanero.delay()
        mock_actualizar.assert_called_once()


class UtilidadesTestCase(TestCase):
    @patch('api.utils.requests.get')
    def test_obtener_valor_dolar_exito_primaria(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'serie': [
                {
                    'valor': 750.0,
                    'fecha': '2024-11-21T00:00:00Z'
                }
            ]
        }
        from .utils import obtener_valor_dolar
        valor, fecha = obtener_valor_dolar()
        self.assertEqual(valor, 750.0)
        self.assertEqual(fecha, '2024-11-21T00:00:00Z')

    @patch('api.utils.requests.get')
    def test_obtener_valor_dolar_respaldo(self, mock_get):
        # Simular fallo en la API primaria y éxito en la de respaldo
        mock_get.side_effect = [
            requests.exceptions.RequestException,
            requests.models.Response()
        ]
        # Configurar el mock de la API de respaldo
        mock_respaldo = mock_get.return_value
        mock_respaldo.raise_for_status.return_value = None
        mock_respaldo.json.return_value = {"Valor": "700,0", "Fecha": "2024-11-21"}
        from .utils import obtener_valor_dolar
        valor, fecha = obtener_valor_dolar()
        self.assertEqual(valor, 700.0)
        self.assertEqual(fecha, "2024-11-21")

    @patch('api.utils.requests.get')
    def test_obtener_valor_dolar_falla_todas_las_apis(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException
        from .utils import obtener_valor_dolar
        valor, fecha = obtener_valor_dolar()
        self.assertIsNone(valor)
        self.assertIsNone(fecha)


class UsuarioAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(
            username="usuario_api",
            password="password123",
            email="usuario_api@example.com",
            telefono="111222333",
            direccion="Calle API 123"
        )
        self.url = reverse('token_obtain_pair')

    def test_obtener_token_concredenciales_correctas(self):
        data = {
            "username": "usuario_api",
            "password": "password123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtener_token_concredenciales_incorrectas(self):
        data = {
            "username": "usuario_api",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_refrescar_token(self):
        refresh = RefreshToken.for_user(self.usuario)
        url_refresh = reverse('token_refresh')
        data = {
            "refresh": str(refresh)
        }
        response = self.client.post(url_refresh, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class SerializerTestCase(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="serializer_user",
            password="password123",
            email="serializer@example.com",
            telefono="444555666",
            direccion="Calle Serializer 456"
        )
        self.producto = Producto.objects.create(
            nombre="Producto Serializer",
            descripcion="Descripción Serializer",
            marca="Marca Serializer",
            precio_usd=Decimal('200.0'),
            peso_kg=Decimal('4.0'),
            disponible=True
        )

    def test_usuario_serializer(self):
        from .serializers import UsuarioSerializer
        serializer = UsuarioSerializer(instance=self.usuario)
        data = serializer.data
        self.assertEqual(data['username'], "serializer_user")
        self.assertEqual(data['email'], "serializer@example.com")
        self.assertEqual(data['telefono'], "444555666")
        self.assertEqual(data['direccion'], "Calle Serializer 456")

    def test_producto_serializer(self):
        from .serializers import ProductoSerializer
        serializer = ProductoSerializer(instance=self.producto)
        data = serializer.data
        self.assertEqual(data['nombre'], "Producto Serializer")
        self.assertEqual(data['precio_usd'], "200.00")
        self.assertEqual(data['peso_kg'], "4.00")

    def test_user_registration_serializer_valida(self):
        from .serializers import UserRegistrationSerializer
        data = {
            "username": "nuevo_serial_user",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "nuevo_serial@example.com",
            "telefono": "777888999",
            "direccion": "Calle Serial 789",
            "password": "SecurePass123",
            "password2": "SecurePass123"
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, "nuevo_serial_user")
        self.assertTrue(user.check_password("SecurePass123"))

    def test_user_registration_serializer_password_mismatch(self):
        from .serializers import UserRegistrationSerializer
        data = {
            "username": "mismatch_user",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "mismatch@example.com",
            "telefono": "000111222",
            "direccion": "Calle Mismatch 101",
            "password": "Password123",
            "password2": "DifferentPassword123"
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_change_password_serializer_valida(self):
        from .serializers import ChangePasswordSerializer
        data = {
            "old_password": "password123",
            "new_password": "NewPass456"
        }
        serializer = ChangePasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_change_password_serializer_no_valida(self):
        from .serializers import ChangePasswordSerializer
        data = {
            "old_password": "wrongpassword",
            "new_password": "NewPass456"
        }
        serializer = ChangePasswordSerializer(data=data)
        # Aunque la validación de las contraseñas ocurre en la vista, el serializer solo valida los campos
        self.assertTrue(serializer.is_valid())
