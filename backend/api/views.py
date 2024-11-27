from rest_framework import viewsets, permissions, generics, filters
from rest_framework.views import APIView
from .models import Producto, Pedido, DetallePedido, Notificacion, Configuracion
from .serializers import (
    ProductoSerializer, PedidoSerializer, NotificacionSerializer, UserRegistrationSerializer, 
    UserProfileSerializer, ConfiguracionSerializer, ChangePasswordSerializer, DetallePedidoSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['marca', 'disponible']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio_usd', 'peso_kg']
    ordering = ['id']

    def perform_create(self, serializer):
        # Solo permitir que el personal shopper (administrador) cree productos
        if self.request.user.is_staff:
            serializer.save()
        else:
            raise PermissionDenied("No tiene permiso para crear productos.")

    def perform_update(self, serializer):
        # Solo permitir que el personal shopper (administrador) actualice productos
        if self.request.user.is_staff:
            serializer.save()
        else:
            raise PermissionDenied("No tiene permiso para actualizar productos.")

    def perform_destroy(self, instance):
        if self.request.user.is_staff:
            instance.delete()
        else:
            raise PermissionDenied("No tiene permiso para eliminar productos.")

class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Pedido.objects.none()
        return Pedido.objects.filter(cliente=self.request.user).select_related('cliente').prefetch_related('detalles__producto').order_by('id')

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notificacion.objects.none()
        return Notificacion.objects.filter(usuario=self.request.user).order_by('id')
    
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({
            "message": "Usuario creado exitosamente.",
            "user": UserRegistrationSerializer(user).data
        }, status=status.HTTP_201_CREATED, headers=headers)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class ConfiguracionViewSet(viewsets.ModelViewSet):
    queryset = Configuracion.objects.all().order_by('id')
    serializer_class = ConfiguracionSerializer
    permission_classes = [permissions.IsAdminUser]

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": "La contraseña actual no es correcta."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)

class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class DetallePedidoViewSet(viewsets.ModelViewSet):
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DetallePedido.objects.none()
        
        user = self.request.user
        if not user.is_authenticated:
            return DetallePedido.objects.none()
        
        return DetallePedido.objects.filter(pedido__cliente=user)

    def perform_create(self, serializer):
        pedido = serializer.validated_data['pedido']
        if pedido.cliente != self.request.user:
            raise PermissionDenied("No tienes permiso para agregar detalles a este pedido.")
        serializer.save()
        pedido.actualizar_totales()
        pedido.calcular_impuesto_aduanero()

    def perform_update(self, serializer):
        pedido = serializer.validated_data.get('pedido', serializer.instance.pedido)
        if pedido.cliente != self.request.user:
            raise PermissionDenied("No tienes permiso para actualizar detalles de este pedido.")
        serializer.save()
        pedido.actualizar_totales()
        pedido.calcular_impuesto_aduanero()

    def perform_destroy(self, instance):
        pedido = instance.pedido
        if pedido.cliente != self.request.user:
            raise PermissionDenied("No tienes permiso para eliminar detalles de este pedido.")
        instance.delete()
        pedido.actualizar_totales()
        pedido.calcular_impuesto_aduanero()
