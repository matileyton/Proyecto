from celery import shared_task
from api.models import Configuracion

@shared_task
def tarea_actualizar_dolar_aduanero():
    configuracion, created = Configuracion.objects.get_or_create(id=1)
    configuracion.actualizar_dolar_aduanero()
