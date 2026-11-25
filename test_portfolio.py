"""Pruebas automatizadas con `assert` para `cartera.py` y `proyecciones.py`.

Permite ejecutar `python test_portfolio.py` y verificar que toda la lógica
funciona correctamente sin depender de la entrada manual por teclado.
"""

import cartera
import proyecciones


def probar_validacion_pesos() -> None:
    """Comprueba casos válidos, límites y erróneos en `validar_pesos_objetivo`."""
    # Cartera vacía: debe devolver False.
    assert cartera.validar_pesos_objetivo([]) is False

    # Suma exacta de 100 %: debe devolver True.
    activos_validos = [
        {"ticker": "MSCIW", "peso_objetivo": 60.0},
        {"ticker": "MSCIE", "peso_objetivo": 25.0},
        {"ticker": "TECH", "peso_objetivo": 15.0},
    ]
    assert cartera.validar_pesos_objetivo(activos_validos) is True

    # Suma dentro de tolerancia decimal (99.999 %): debe devolver True.
    activos_tolerancia = [
        {"ticker": "A", "peso_objetivo": 33.333},
        {"ticker": "B", "peso_objetivo": 33.333},
        {"ticker": "C", "peso_objetivo": 33.333},
    ]
    assert cartera.validar_pesos_objetivo(activos_tolerancia) is True

    # Suma incorrecta (90 %): debe devolver False.
    activos_invalidos = [
        {"ticker": "MSCIW", "peso_objetivo": 60.0},
        {"ticker": "MSCIE", "peso_objetivo": 30.0},
    ]
    assert cartera.validar_pesos_objetivo(activos_invalidos) is False


def probar_registro_y_valoracion() -> None:
    """Comprueba la mutación de la lista al registrar compras y el precio medio."""
    activos: list[dict] = []

    # Cartera vacía: todos los indicadores deben ser 0.0.
    assert cartera.valorar_cartera(activos) == (0.0, 0.0, 0.0)

    # Primera compra de MSCIW: 10 uds a 100.0 -> invertido = 1000.0.
    cartera.registrar_operacion(activos, " msciw ", "MSCI World", 10, 100.0, 60.0)
    assert len(activos) == 1
    assert activos[0]["ticker"] == "MSCIW"

    # Segunda compra del mismo ticker: 10 uds a 120.0.
    # No debe duplicar el activo, sino promediar compra: (1000 + 1200) / 20 = 110.0.
    cartera.registrar_operacion(activos, "MSCIW", "MSCI World", 10, 120.0, 60.0)
    assert len(activos) == 1
    assert activos[0]["unidades"] == 20.0
    assert activos[0]["precio_compra"] == 110.0
    assert activos[0]["precio_actual"] == 120.0

    # Valoración: invertido = 20 * 110 = 2200.0; actual = 20 * 120 = 2400.0.
    invertido, actual, rentabilidad = cartera.valorar_cartera(activos)
    assert invertido == 2200.0
    assert actual == 2400.0
    assert round(rentabilidad, 2) == 9.09


def probar_rebalanceo_y_no_mutacion() -> None:
    """Verifica el reparto proporcional al déficit y que `activos` no se muta."""
    activos = [
        {
            "ticker": "MSCIW",
            "nombre": "MSCI World",
            "unidades": 8.0,
            "precio_compra": 100.0,
            "precio_actual": 100.0,  # 800 € actuales (80 %) -> sobreponderado vs 60 %
            "peso_objetivo": 60.0,
        },
        {
            "ticker": "MSCIE",
            "nombre": "Emerging Markets",
            "unidades": 2.0,
            "precio_compra": 100.0,
            "precio_actual": 100.0,  # 200 € actuales (20 %) -> infraponderado vs 40 %
            "peso_objetivo": 40.0,
        },
    ]

    # Guardamos una copia superficial para confirmar que la lista original no cambia.
    copia_seguridad = [activo.copy() for activo in activos]

    # Con 1000 € actuales + 250 € de aportación = 1250 € futuros:
    # Objetivo futuro MSCIW (60 %) = 750 € (ya tiene 800 € -> déficit 0).
    # Objetivo futuro MSCIE (40 %) = 500 € (tiene 200 € -> déficit 300).
    # Toda la aportación de 250 € debe ir a MSCIE.
    plan = cartera.calcular_rebalanceo(activos, 250.0)

    assert activos == copia_seguridad
    assert plan[0]["ticker"] == "MSCIW"
    assert plan[0]["aportar"] == 0.0
    assert plan[1]["ticker"] == "MSCIE"
    assert plan[1]["aportar"] == 250.0

    # Caso borde: aportación 0.0 -> aporta 0.0 a todos sin fallar.
    plan_cero = cartera.calcular_rebalanceo(activos, 0.0)
    assert plan_cero[0]["aportar"] == 0.0
    assert plan_cero[1]["aportar"] == 0.0


def probar_proyecciones_iterativo_vs_recursivo() -> None:
    """Comprueba que iteración y recursividad dan el mismo resultado."""
    # Caso base: 0 meses -> debe devolver exactamente el capital inicial.
    assert proyecciones.interes_compuesto_iterativo(1000.0, 200.0, 0.07, 0) == 1000.0
    assert proyecciones.interes_compuesto_recursivo(1000.0, 200.0, 0.07, 0) == 1000.0

    # Caso sin rentabilidad (0 % anual) durante 12 meses: 1000 + 12 * 100 = 2200.0.
    res_it_cero = proyecciones.interes_compuesto_iterativo(1000.0, 100.0, 0.0, 12)
    res_rec_cero = proyecciones.interes_compuesto_recursivo(1000.0, 100.0, 0.0, 12)
    assert round(res_it_cero, 2) == 2200.00
    assert round(res_rec_cero, 2) == 2200.00

    # Caso estándar con interés compuesto (24 meses al 8 % anual): ambos deben coincidir.
    res_it = proyecciones.interes_compuesto_iterativo(5000.0, 300.0, 0.08, 24)
    res_rec = proyecciones.interes_compuesto_recursivo(5000.0, 300.0, 0.08, 24)
    assert round(res_it, 4) == round(res_rec, 4)


def probar_errores_controlados() -> None:
    """Comprueba que se lanzan `ValueError` ante datos inválidos."""
    # Unidades negativas al registrar operación.
    try:
        cartera.registrar_operacion([], "AAPL", "Apple", -2, 150.0, 100.0)
        assert False, "Debió lanzar ValueError por unidades negativas"
    except ValueError:
        pass

    # Rebalanceo con aportación negativa.
    try:
        cartera.calcular_rebalanceo([{"ticker": "A", "unidades": 1, "precio_compra": 10, "precio_actual": 10, "peso_objetivo": 100.0}], -50.0)
        assert False, "Debió lanzar ValueError por aportación negativa"
    except ValueError:
        pass

    # Proyección con meses negativos.
    try:
        proyecciones.interes_compuesto_recursivo(1000.0, 100.0, 0.05, -3)
        assert False, "Debió lanzar ValueError por meses negativos"
    except ValueError:
        pass


def ejecutar_todas_las_pruebas() -> None:
    """Ejecuta todas las baterías de prueba e informa si todo pasa."""
    probar_validacion_pesos()
    probar_registro_y_valoracion()
    probar_rebalanceo_y_no_mutacion()
    probar_proyecciones_iterativo_vs_recursivo()
    probar_errores_controlados()
    print("Todas las pruebas con assert se han superado correctamente.")


if __name__ == "__main__":
    ejecutar_todas_las_pruebas()