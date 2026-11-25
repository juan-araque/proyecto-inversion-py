"""Módulo de proyecciones financieras mediante iteración y recursividad.

Permite comparar cómo evoluciona un capital con aportaciones periódicas
usando un bucle (`for`) frente a una función recursiva con caso base.
"""


def _validar_parametros_proyeccion(
    capital: float,
    aporte_mensual: float,
    tasa_anual: float,
    meses: int,
) -> None:
    
    """Valida que los parámetros de la proyección tengan valores coherentes.

    Separar esta validación en una función auxiliar evita repetir los mismos
    `if ... raise ValueError` tanto en la versión iterativa como en la recursiva.
    """
    # El capital inicial no puede ser negativo, 0.0 si es valido
    if capital < 0 :
        raise ValueError ("El capital inicial no puede ser negativo.")

    if aporte_mensual < 0:
        raise ValueError("El aporte mensual no puede ser negativo")

    if tasa_anual <= -1.0:
        raise ValueError("La tasa anual debe ser mayor que -100 % (-1.0)")

   # El número de meses debe ser entero y nunca negativo.
    # Comprobamos isinstance(meses, bool) porque en Python bool es subclase de int.
    if isinstance(meses, bool) or not isinstance(meses, int) or meses < 0:
        raise ValueError("El número de meses debe ser un entero mayor o igual que 0.")



def interes_compuesto_iterativo(
        capital: float,
    aporte_mensual: float,
    tasa_anual: float,
    meses: int,
) -> float:
    
    """Calcula el capital final mediante un bucle mes a mes.

    Parámetros:
        capital: Capital inicial disponible.
        aporte_mensual: Cantidad añadida al final de cada mes.
        tasa_anual: Rentabilidad anual en formato decimal (ej. 0.07 para un 7 %).
        meses: Horizonte temporal en meses (>= 0).

    Retorna:
        Capital acumulado tras `meses` meses.
    """

    # Validamos los parametros antes de iniciar el calculo
    _validar_parametros_proyeccion(capital, aporte_mensual, tasa_anual, meses)

    # Convertimos la tasa anual en tasa efectiva mensual aprox
    tasa_mensual = tasa_anual / 12


    # Usamos una variable local acumuladora para no depender de variables globales.
    # Como `capital` es un float (inmutable), modificar `saldo` aquí no altera
    # ninguna variable que exista fuera de esta función.
    saldo = float(capital)

    # Repetimos el proceso una vez por cada mes transcurrido.
    for _ in range (meses):
        # 1. Generamos los intereses del mes sobre el saldo actual.
        # 2. Sumamos la nueva aportación mensual.
        saldo = saldo * (1.0 + tasa_mensual) + aporte_mensual

    return saldo

def interes_compuesto_recursivo(
    capital: float,
    aporte_mensual: float,
    tasa_anual: float,
    meses: int,
) -> float:
    
    """Calcula el capital final de forma recursiva reduciendo el plazo en 1 mes.

    Parámetros:
        capital: Capital acumulado hasta el momento actual.
        aporte_mensual: Cantidad añadida en cada mes.
        tasa_anual: Rentabilidad anual en formato decimal (ej. 0.07 para un 7 %).
        meses: Meses restantes por simular (>= 0).

    Retorna:
        Capital acumulado tras `meses` meses.
    """

    # Validamos también aquí para que si alguien llama directamente a la función
    # recursiva con datos inválidos reciba error de inmediato.
    _validar_parametros_proyeccion(capital, aporte_mensual, tasa_anual, meses)

    # CASO BASE: si quedan 0 meses por simular, ya no hay más periodos que calcular
    # y devolvemos el capital actual tal cual. Esto detiene la recursión.
    if meses == 0:
        return float(capital)

    # Calculamos el estado tras un solo mes.
    tasa_mensual = tasa_anual / 12.0
    capital_tras_un_mes = capital * (1.0 + tasa_mensual) + aporte_mensual

    # CASO RECURSIVO: llamamos a la misma función con `meses - 1` (acercándonos
    # al caso base `meses == 0`) y pasando el nuevo capital acumulado.
    return interes_compuesto_recursivo(
        capital=capital_tras_un_mes,
        aporte_mensual=aporte_mensual,
        tasa_anual=tasa_anual,
        meses=meses - 1,
    )