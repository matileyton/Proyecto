from rest_framework import serializers
from .models import Producto, Usuario, Pedido, DetallePedido, Notificacion, Configuracion
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'telefono', 'direccion']

class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirmar contraseña')

    class Meta:
        model = Usuario
        fields = ['username','first_name', 'last_name', 'email', 'telefono', 'direccion', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            telefono=validated_data.get('telefono', ''),
            direccion=validated_data.get('direccion', ''),
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'telefono', 'direccion', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

    def validate(self, data):
        precio_usd = data.get('precio_usd')
        precio_final_clp = data.get('precio_final_clp')
        if not precio_usd and not precio_final_clp:
            raise serializers.ValidationError("Debes ingresar el precio en USD o el precio final en CLP.")
        return data

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'cantidad', 'subtotal_usd', 'subtotal_clp', 'peso_kg']
        read_only_fields = ['subtotal_usd', 'subtotal_clp', 'peso_kg']

class PedidoSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    detalles = DetallePedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'fecha_pedido', 'estado', 'total_usd', 'total_clp',
            'peso_total_kg', 'valor_dolar', 'total_final_clp', 'detalles'
        ]
        read_only_fields = ['id', 'fecha_pedido', 'total_usd', 'total_clp',
                            'peso_total_kg', 'valor_dolar', 'total_final_clp']

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        pedido = Pedido.objects.create(cliente=self.context['request'].user, **validated_data)
        for detalle_data in detalles_data:
            producto = detalle_data['producto']
            cantidad = detalle_data['cantidad']
            DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)
        pedido.actualizar_totales()
        pedido.calcular_impuesto_aduanero()
        return pedido

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)
        # Actualizar campos del pedido si es necesario
        instance.estado = validated_data.get('estado', instance.estado)
        instance.save()

        if detalles_data is not None:
            # Opcional: Manejar actualización de detalles (ejemplo simple: eliminar y recrear)
            instance.detalles.all().delete()
            for detalle_data in detalles_data:
                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']
                DetallePedido.objects.create(pedido=instance, producto=producto, cantidad=cantidad)
            instance.actualizar_totales()
            instance.calcular_impuesto_aduanero()

        return instance

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'

class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = '__all__'

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agregar campos personalizados al token
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token
