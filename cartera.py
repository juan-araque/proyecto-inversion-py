""" Modulo para gestionar una cartera de inversion y calcular su rebalanceo.
Contiene funciones puras de calculo/validacioon y una funcion que muta la lista de activos recibida
para registrar operaciones, permitiendo prcticar el paso por objetos mutables, control de errores y separacion de
responsabilidades.
"""
def validar_pesos_objetivo(activos: list[dict], tolerancia: float = 0.01) -> bool:
    """ Comprueba si los porcentajes de los activos sumas 100%
    
    Parámetros:
        activos: Lista de diccionarios donde cada elemento representa un activo
        tolerancia: margen decimal permitido para evitar fallos por coma flotante

    Return:
        True si la suma esta dentro del margen respecto a 100.0. False en caso contrario
    """
    # Comprobar primero para evitar trabajar sobre una cartera vacia
    if not activos:
        return False

    #Sumamos el campo 'peso_objetivo' de todos los diccionarios de la lista
    total_pesos = sum(activo["peso_objetivo"] for activo in activos)

    return abs(total_pesos - 100) <= tolerancia

def valorar_cartera(activos: list[dict]) -> tuple[float,float,float]:
    """ Calcular el capital invertido, el valor actual y la rentabilidad porcentual

    Parametros:
        activos: lista de diccionarios con unidades, precio de compra y precio actual

    Return:
        Una tupla con (capital_invertido, valor_actual, rentabilidad_porcentaje) 
    """

    #Caso Limite: si no hay activos, devolvemos ceros en vez de dar error
    if not activos:
        return 0.0, 0.0, 0.0

    # Capital total desembolsado históricamente: unidades * precio medio de compra.
    invertido = sum(activo["unidades"] * activo ["precio_compra"] for activo in activos)


    # Valoración actual a mercado: unidades * precio actual de cada activo.
    valor_actual = sum(activo["unidades"] * activo["precio_actual"] for activo in activos)

    if invertido == 0:
        rentabilidad_pct= 0.0
    else:
        # Rentabilidad relativa en porcentaje: ((Valor actual - Coste) / Coste) * 100.
        rentabilidad_pct = ((valor_actual - invertido)/ invertido ) * 100

    return invertido, valor_actual, rentabilidad_pct

def registrar_operacion(
    activos: list[dict],
    ticker: str,
    nombre: str,
    unidades: float,
    precio: float,
    peso_objetivo: float,
) -> None:
    """Registra una compra nueva o actualiza una posicion existente en la cartera.

    Esta funcion MODIFICA directamente la lista 'activos' recibida (objeto mutable)

    Parametros:
        activos: Lista mutable de activos de la cartera.
        ticker: Código identificativo del activo (ej. 'VWCE', 'MSFT').
        nombre: Nombre descriptivo del activo.
        unidades: Cantidad de participaciones/acciones compradas (> 0).
        precio: Precio unitario de la operación (> 0).
        peso_objetivo: Porcentaje objetivo deseado en la cartera (entre 0 y 100).
    """
    # Validadmos los datos de entrada dentro de la funcion para que no entren datos 
    # invalidos y se lance un ValueError
    if unidades <= 0 or precio <= 0:
        raise ValueError ("Las uniades y el precio deben ser mayores que cero.")

    if peso_objetivo < 0 or peso_objetivo > 100:
        raise ValueError ("El peso objetivo debe estar entre 0 y 100.")

    # Normalizamos el ticker sin espacios y en mayusculas
    ticker_limpio = ticker.strip().upper()

    # Buscamos si el activo existe en la lista 'activos'
    for activo in activos:
        if activo["ticker"] == ticker_limpio:
            # Guardamos las unidades y el coste previo antes de actualizar.
            unidades_anteriores = activo["unidades"]
            coste_anterior = unidades_anteriores * activo ["precio_compra"]

            # Calculamos el coste de esta nueva compra y el total de unidades
            coste_nuevo = unidades * precio
            nuevas_unidades = unidades_anteriores + unidades

            # Recalculamos el precio medio ponderado de compra:
            # (Coste total anterior + Coste compra nueva) / Total unidades nuevas.
            activo["precio_compra"] = (coste_anterior + coste_nuevo) / nuevas_unidades
            activo["unidades"] = nuevas_unidades

            # Actualizamos el precio de referencia y el peso objetivo al último indicado.
            activo["precio_actual"] = precio
            activo["peso_objetivo"] = peso_objetivo

            # Salimos de la función con return porque ya actualizamos el activo existente;
            # así evitamos que luego se añada como un elemento duplicado al final.
            return

    # Si el bucle termina sin encontrar el ticker, creamos un nuevo diccionario
    # y lo añadimos a la lista original mediante .append().
    # Como `activos` es una lista (objeto mutable), el cambio se refleja fuera.
    activos.append(
        {
            "ticker": ticker_limpio,
            "nombre": nombre.strip(),
            "unidades": float(unidades),
            "precio_compra": float(precio),
            "precio_actual": float(precio),
            "peso_objetivo": float(peso_objetivo),
        }
    )

def calcular_rebalanceo(activos: list[dict], aportacion: float) -> list[dict]:
    """Calcula cómo repartir una nueva aportación según los pesos objetivo.

    A diferencia de `registrar_operacion`, esta función NO modifica `activos`:
    construye y devuelve una lista nueva con el plan de reparto.

    Parámetros:
        activos: Lista de activos actuales de la cartera.
        aportacion: Cantidad de dinero nuevo a aportar (>= 0).

    Retorna:
        Lista de diccionarios con el valor actual, peso actual, peso objetivo
        y cantidad recomendada a aportar por cada activo.
    """

    # Comprobaciones previas
    if aportacion < 0:
        raise ValueError("La aportacion no puede ser negativa.")
    if not activos:
        raise ValueError("La cartera esta vacía.")
    if not validar_pesos_objetivo(activos):
        raise ValueError("Los pesos deben sumar 100 %.")

    # Obtenemos el valor actual de la cartera. Usamos _ para ignorar
    # el primer y tercer valor de la tupla (invertido y rentabilidad), 
    # que aqui no usamos

    _, valor_actual_total, _ = valorar_cartera(activos)

    # Valor total que tendra la cartera si sumamos toda la nueva aportacion
    objetivo_total_futuro = valor_actual_total + aportacion

    # Calculamos cuanto le falta a cada activo para alcanzar su peso objetivo
    # sobre el tamaño futuro de la cartera
    deficits = []

    for activo in activos:
        valor_actual = activo["unidades"] * activo["precio_actual"]
        valor_deseado = objetivo_total_futuro * (activo["peso_objetivo"] / 100.0)

        # max 0.0 garantiza que un activo sobreponderado tenga deficit de 0.0 en vez de negativo
        deficit = max (0.0, valor_deseado - valor_actual)
        deficits.append(deficit)

    # suma de todos los deficits positivos para repartir la aportacion de forma proporcional
    suma_deficits = sum(deficits)
    plan = []

    for indice, activo in enumerate(activos):
        valor_actual = activo["unidades"] * activo["precio_actual"]

        # Calculamos el peso real (%) de este activo dentro de la cartera
        peso_actual = (
            (valor_actual / valor_actual_total) * 100.0
            if valor_actual_total > 0
            else 0.0
        )

        # Determinamos cuanto dinero de la aportacion asignar a este activo:

        if aportacion == 0:
            # Si no se aporta dinero nuevo, no se compra nada en ningún activo.
            asignacion = 0.0
        elif suma_deficits > 0:
            # Repartimos proporcionalmente al déficit de cada activo respecto al total.
            asignacion = aportacion * (deficits[indice] / suma_deficits)
        else:
            asignacion = aportacion * (activo["peso_objetivo"] / 100.0)

        # Guardamos el resultado en una nueva estructura sin tocar `activos`.
        plan.append(
            {
                "ticker": activo["ticker"],
                "valor_actual": round(valor_actual, 2),
                "peso_actual": round(peso_actual, 2),
                "peso_objetivo": round(activo["peso_objetivo"], 2),
                "aportar": round(asignacion, 2),
            }
        )

    return plan