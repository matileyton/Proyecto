from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.utils import timezone

class Configuracion(models.Model):
    porcentaje_comision = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.0'))
    tasa_seguro = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    costo_por_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.0'))
    tasa_arancel = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('6.0'))
    tasa_iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('19.0'))
    dolar_aduanero = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_actualizacion_dolar_aduanero = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Configuración - Comisión: {self.porcentaje_comision}%"

    def actualizar_dolar_aduanero(self):
        from .utils import obtener_dolar_aduanero
        valor = obtener_dolar_aduanero()
        if valor:
            self.dolar_aduanero = valor
            self.fecha_actualizacion_dolar_aduanero = timezone.now()
            self.save()

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    marca = models.CharField(max_length=50)
    precio_usd = models.DecimalField(max_digits=10, decimal_places=2)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)  # Peso en kilogramos
    fecha_compra = models.DateField(null=True, blank=True)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    precio_final_clp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.marca}"
    
    @property
    def precio_clp(self):
        if self.precio_final_clp:
            return self.precio_final_clp
        else:
            from .utils import obtener_valor_dolar
            valor_dolar, _ = obtener_valor_dolar()
            if valor_dolar:
                configuracion = Configuracion.objects.first()
                porcentaje_comision = configuracion.porcentaje_comision if configuracion else Decimal('0')
                precio_usd_con_comision = self.precio_usd + (self.precio_usd * porcentaje_comision / Decimal('100.0'))
                return precio_usd_con_comision * Decimal(valor_dolar)
            else:
                return Decimal('0')

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username

class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('recibido', 'Recibido'),
        ('en_proceso', 'En proceso'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='recibido')
    total_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_clp = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    peso_total_kg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valor_dolar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comprobante_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    total_final_clp = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"

    def save(self, *args, **kwargs):
        if not self.id:
            from .utils import obtener_valor_dolar
            valor_dolar, _ = obtener_valor_dolar()
            if valor_dolar:
                self.valor_dolar = Decimal(valor_dolar)
            else:
                self.valor_dolar = Decimal('0')
        super().save(*args, **kwargs)

    def actualizar_totales(self):
        detalles = self.detalles.all()
        self.total_usd = sum(det.subtotal_usd for det in detalles)
        self.peso_total_kg = sum(det.peso_kg for det in detalles)
        self.total_clp = sum(det.subtotal_clp for det in detalles)
        self.save()

    def calcular_seguro(self):
        configuracion = Configuracion.objects.first()
        tasa_seguro = configuracion.tasa_seguro if configuracion else Decimal('0')
        return (self.total_usd * tasa_seguro) / Decimal('100.0')

    def calcular_flete(self):
        configuracion = Configuracion.objects.first()
        costo_por_kg = configuracion.costo_por_kg if configuracion else Decimal('0')
        return self.peso_total_kg * costo_por_kg

    def calcular_impuesto_aduanero(self):
        configuracion = Configuracion.objects.first()
        if configuracion and configuracion.dolar_aduanero:
            dolar_aduanero = configuracion.dolar_aduanero

            tasa_arancel = configuracion.tasa_arancel
            tasa_iva = configuracion.tasa_iva

            valor_cif_usd = self.total_usd + self.calcular_seguro() + self.calcular_flete()
            valor_cif_clp = valor_cif_usd * dolar_aduanero

            arancel = (valor_cif_clp * tasa_arancel) / Decimal('100.0')
            iva_importacion = ((valor_cif_clp + arancel) * tasa_iva) / Decimal('100.0')

            total_impuestos = arancel + iva_importacion

            self.total_final_clp = self.total_clp + total_impuestos
            self.save()

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal_clp = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        self.subtotal_usd = self.cantidad * self.producto.precio_usd
        self.peso_kg = self.cantidad * self.producto.peso_kg

        if self.producto.precio_final_clp:
            self.subtotal_clp = self.cantidad * self.producto.precio_final_clp
        else:
            if self.pedido.valor_dolar:
                configuracion = Configuracion.objects.first()
                porcentaje_comision = configuracion.porcentaje_comision if configuracion else Decimal('0')
                precio_usd_con_comision = self.producto.precio_usd + (self.producto.precio_usd * porcentaje_comision / Decimal('100.0'))
                precio_clp = precio_usd_con_comision * self.pedido.valor_dolar
                self.subtotal_clp = self.cantidad * precio_clp
            else:
                self.subtotal_clp = Decimal('0')

        super().save(*args, **kwargs)

class Notificacion(models.Model):
    TIPO_NOTIFICACION = [
        ('estado_pedido', 'Estado de Pedido'),
        ('promocion', 'Promoción'),
        ('otro', 'Otro'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_NOTIFICACION)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.usuario.username} - {self.tipo}"
