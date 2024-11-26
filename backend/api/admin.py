from django.contrib import admin
from .models import Producto, Usuario, Pedido, DetallePedido, Notificacion, Configuracion

admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Notificacion)
admin.site.register(Configuracion)
