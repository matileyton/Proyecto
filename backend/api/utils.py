import requests
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal

def obtener_valor_dolar():
    url_primaria = 'https://mindicador.cl/api/dolar'
    url_respaldo = 'https://api.gael.cloud/general/public/monedas/USD'
    
    try:
        respuesta = requests.get(url_primaria, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        valor_dolar = datos['serie'][0]['valor']
        fecha = datos['serie'][0]['fecha']
        return valor_dolar, fecha
    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Error al obtener el valor del dólar de la API primaria: {e}")
        try:
            respuesta = requests.get(url_respaldo, timeout=10)
            respuesta.raise_for_status()
            datos = respuesta.json()
            valor_dolar = float(datos['Valor'].replace(',', '.'))
            fecha = datos['Fecha']
            return valor_dolar, fecha
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"Error al obtener el valor del dólar de la API de respaldo: {e}")
            return None, None

def obtener_dolar_aduanero():
    url = 'https://www.pollmann.cl/parametros.php?tipo=5'
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()  # Verifica que la solicitud fue exitosa
        soup = BeautifulSoup(respuesta.content, 'html.parser')

        # Encuentra la tabla que contiene los datos
        tabla = soup.find('table', {'cellpadding': '2', 'cellspacing': '2', 'border': '1', 'align': 'left'})
        if not tabla:
            print("No se pudo encontrar la tabla en la página.")
            return None

        # Obtener el mes actual en español
        meses_espanol = {
            1: 'Enero',
            2: 'Febrero',
            3: 'Marzo',
            4: 'Abril',
            5: 'Mayo',
            6: 'Junio',
            7: 'Julio',
            8: 'Agosto',
            9: 'Septiembre',
            10: 'Octubre',
            11: 'Noviembre',
            12: 'Diciembre'
        }
        mes_actual = meses_espanol[datetime.now().month]

        # Buscar la fila que corresponde al mes actual
        filas = tabla.find_all('tr')
        for fila in filas:
            celdas = fila.find_all('td')
            if len(celdas) >= 4:
                mes = celdas[1].get_text(strip=True)
                valor_texto = celdas[2].get_text(strip=True)
                if mes == mes_actual:
                    # Convierte el valor a Decimal, eliminando cualquier separador de miles o símbolo
                    valor_dolar_aduanero = Decimal(valor_texto.replace('.', '').replace(',', '.'))
                    return valor_dolar_aduanero
        print(f"No se encontró el valor del dólar aduanero para el mes de {mes_actual}.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud: {e}")
        return None
    
if __name__ == '__main__':
    valor_dolar, fecha = obtener_valor_dolar()
    if valor_dolar:
        print(f"El valor del dólar es {valor_dolar} CLP al {fecha}")
    valor_dolar_aduanero = obtener_dolar_aduanero()
    if valor_dolar_aduanero:
        print(f"El valor del dólar aduanero es {valor_dolar_aduanero} CLP")
