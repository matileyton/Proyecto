from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoViewSet, 
    PedidoViewSet, 
    NotificacionViewSet, 
    UserRegistrationView, 
    UserProfileView,  
    ConfiguracionViewSet, 
    ChangePasswordView, 
    DeleteAccountView, 
    DetallePedidoViewSet
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')
router.register(r'configuracion', ConfiguracionViewSet, basename='configuracion')
router.register(r'detalles', DetallePedidoViewSet, basename='detallepedido')

urlpatterns = [
    path('', include(router.urls)),
    path('users/register/', UserRegistrationView.as_view(), name='user-register'),
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/delete/', DeleteAccountView.as_view(), name='delete-account'),
]
