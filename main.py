"""Programa principal del simulador de cartera de inversión y rebalanceo.

Separa la interfaz de consola (lectura de datos, menús, formato de salida y
captura de errores de entrada) de la lógica de negocio en `cartera.py` y
`proyecciones.py`.
"""
import cartera
import proyecciones

def mostrar_menu() -> None:
    """ Muestra las opciones disponibles del menu"""
    print("\n === SIMULADOR DE CARTERA Y REBALANCEO ===")
    print("1. Registrar compra o actualizar activo")
    print("2. Ver resumen de rentabilidad de la cartera")
    print("3. Calcular plan de rebalanceo con nueva aportacion")
    print("4. Proyectar interés compuesto (iterativo vs. recursivo)")
    print("5. Salir.")

def leer_texto_no_vacio(mensaje: str) -> str:
    """ Solicita una cadena de texto y evita que quede vacia o con espacios"""
    # Repetimos hasta que el usuario escriba algo valido
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("Error: este campo no puede estar vacio.")

def leer_float(mensaje : str, minimo: float | None = None, mayor_que : float | None = None) -> float:
    """ Solicita un numero decimal/real y valida limites opcionales con try-except"""
    while True:
        # Sustituimos coma por punto por si el usuario escribe decimales en formato español (ej. 12,5).
        entrada = input(mensaje).strip().replace(",",".")
        try:
            valor = float (entrada)
        except ValueError:
            print("Error: debes introducir un valor numerico valido")
            continue

        if mayor_que is not None and valor <= mayor_que:
            print(f"Error: el valor debe ser mayor que {mayor_que:g}")
            continue
        if minimo is not None and valor < minimo:
            print(f"Error: el valor no puede ser menor que {minimo:g}")
            continue

        return valor

def leer_entero(mensaje : str, minimo : int | None = None) -> int:
    """ Solicita un numero entero y controla entradas invisibles o fuera de rango"""
    while True:
        entrada = input(mensaje).strip()
        try:
            valor = int(entrada)
        except ValueError:
            print("Error: debes introducir un numero valido")
            continue
        if minimo is not None and valor < minimo:
            print(f"Error: el valor debe ser mayor o igual que {minimo}")
            continue
        return valor

def opcion_registrar_operacion(activos: list[dict]) -> None:
    """Gestion de la opcion 1: pide datos y muta  la lista 'activos' mediante 'registrar'"""
    ticker = leer_texto_no_vacio("Ticker del activo: ")
    nombre = leer_texto_no_vacio("Nombre del activo: ")
    unidades = leer_float("Unidades compradas: ", mayor_que=0.0)
    precio = leer_float("Precio unitario de compra: ", mayor_que=0.0)
    peso_objetivo = leer_float("Peso objetivo de la cartera (0-100 %): ", minimo=0.0)

    # Capturamos ValueError por si alguna regla interna sse dispara
    try:
        cartera.registrar_operacion(
            activos=activos,
            ticker=ticker,
            nombre=nombre,
            unidades=unidades,
            precio=precio,
            peso_objetivo=peso_objetivo,
        )
        print(f"Operacion registrada para {ticker.upper()}")
    except ValueError as error:
        print(f"Error al registrar la operacion {error}")

def opcion_ver_resumen(activos : list[dict]) -> None:
    """Gestiona la opcion 2: muestra posiciones, pesos actuales y rentabilidad total"""
    if not activos:
        print("La cartera esta vacia. Registra al menos algun activo")
        return
    
    invertido, valor_actual, rentabilidad_pct = cartera.valorar_cartera(activos)
    pesos_validos = cartera.validar_pesos_objetivo

    print("\n--- POSICIONES ACTUALES ---")
    for activo in activos:
        posicion_actual = activo["unidades"] * activo["precio_actual"]
        peso_real = (posicion_actual/valor_actual * 100.0) if valor_actual > 0 else 0.0
        print(
            f"{activo['ticker']} ({activo['nombre']}): "
            f"{activo['unidades']:.2f} uds | "
            f"P. compra: {activo['precio_compra']:.2f} | "
            f"P. actual: {activo['precio_actual']:.2f} | "
            f"Valor: {posicion_actual:.2f} | "
            f"Peso real: {peso_real:.2f}% / Obj: {activo['peso_objetivo']:.2f}%"
        ) 

    print("\n--- RESUMEN GLOBAL ---")
    print(f"Capital invertido: {invertido:.2f}")
    print(f"Valor actual:      {valor_actual:.2f}")
    print(f"Rentabilidad:      {rentabilidad_pct:+.2f}%")

    # Avisamos si los pesos objetivos no llegan a 100%
    if not pesos_validos:
        print("Aviso: los pesos actuales no llegan al 100.0 %")

def opcion_rebalancear(activos: list[dict]) -> None:
    """Gestiona la opcion 3: calcula y muestra el reparto de una aportacion"""
    if not activos:
        print("La cartera esta vacia. Añade activos antes de calcular el rebalanceo")
        return

    aportacion = leer_float("Aportacion nueva a invertir: ", minimo=0.0)

    try:
        # calcular_rebalanceo devuelve una lista nueva sin mutar
        plan = cartera.calcular_rebalanceo(activos,aportacion)
    except ValueError as error:
        print(f"No se puede calcular el rebalanceo: {error}")
        return  

    print("\n --- PLAN DE REBALANCEO ---")
    for fila in plan:
        print(
            f"{fila['ticker']}: "
            f"Actual {fila['valor_actual']:.2f} ({fila['peso_actual']:.2f}%) | "
            f"Obj {fila['peso_objetivo']:.2f}% | "
            f"Aportar: {fila['aportar']:.2f}"
        ) 


def opcion_proyectar_interes() -> None:
    """ Gestiona la opcion 4: compara interes compuesto iterativo vs. recursivo"""

    capital = leer_float("Capital inicial: ", minimo=0.0)
    aporte_mensual = leer_float("Aporte mensual: ", minimo=0.0)
    tasa_porcentaje = leer_float("Rentabilidad anual estimada : ")
    meses = leer_entero("Numero de meses a proyectar: ", minimo=0.0)

    # Convertimos el porcentaje introducido por el usuario a decimal
    tasa_anual = tasa_porcentaje / 100.0

    try:
        total_iterativo = proyecciones.interes_compesto_iterativo(
            capital = capital,
            aporte_mensual= aporte_mensual,
            tasa_anual= tasa_anual,
            meses=meses,
        )

        total_recursivo = proyecciones.interes_compuesto_recursivo(
            capital = capital,
            aporte_mensual= aporte_mensual,
            tasa_anual= tasa_anual,
            meses=meses,
        )
    except ValueError as error:
        print(f"Error en la proyeccion: {error} ")
        return

    print("\n --- PROYECCION DE INTERES COMPUESTO ---")
    print(f"Resultado iterativo: {total_iterativo:.2f}")
    print(f"Resultado recursivo: {total_recursivo:.2f}")

def ejecutar_programa() -> None:
    """ Inicializa la cartera y ejecuta el bucle principal hasta elegir salir. """
    # Creamos la lista vacia que guardara los diccionarios de cada activo
    cartera_activos = list[dict] = []

    while True:
        mostrar_menu()
        opcion = input("Selecciona un opcion (1-5): ").strip()

        if opcion == "1":
            opcion_registrar_operacion(cartera_activos)

        elif opcion == "2":
            opcion_ver_resumen(cartera_activos)

        elif opcion == "3":
            opcion_rebalancear(cartera_activos)

        elif opcion == "4":
            opcion_proyectar_interes()

        elif opcion == "5":
            print("Programa finalizado.")
            break

        else:
            print("Opcion no valida. Elige un numero del 1 al 5.")

# Este bloque garantiza que `ejecutar_programa()` solo se ejecute cuando
# lanzamos `python main.py` directamente, y no si alguien importa `main` desde otro archivo.
if __name__ == "__main__":
    ejecutar_programa()
