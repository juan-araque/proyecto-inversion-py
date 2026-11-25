# 📊 Portfolio Tracker & Rebalance CLI

Aplicación de consola modular desarrollada en **Python** para registrar posiciones de inversión (ETFs, fondos o acciones), calcular su rentabilidad global, simular el reparto óptimo de nuevas aportaciones según pesos objetivo y proyectar el crecimiento del capital mediante interés compuesto (comparando un enfoque iterativo frente a uno recursivo).

---

## 🎯 Funcionalidades principales

- **Gestión de cartera (`cartera.py`)**:
  - Registro de compras nuevas y actualización automática de posiciones existentes calculando el **precio medio ponderado**.
  - Validación de que la suma de los pesos objetivo de la cartera sea del `100 %` (con margen de tolerancia decimal).
  - Cálculo de capital invertido, valoración actual y rentabilidad porcentual.
- **Simulación de rebalanceo sin mutación (`cartera.py`)**:
  - Cálculo de aportaciones recomendadas para acercar los activos infraponderados a su peso objetivo sin necesidad de vender posiciones y **sin alterar la cartera original**.
- **Proyecciones financieras (`proyecciones.py`)**:
  - Cálculo de interés compuesto con aportaciones mensuales periódicas implementado mediante dos paradigmas equivalentes: **iteración (`for`)** y **recursividad** (caso base + llamada recursiva).
- **Interfaz CLI y pruebas automatizadas (`main.py` y `test_portfolio.py`)**:
  - Menú interactivo por consola con validación robusta de entradas y captura de excepciones (`try-except`).
  - Batería de pruebas unitarias con `assert` que verifica casos normales, casos borde (`0`), errores controlados (`ValueError`) e integridad de datos.

---

## 📁 Estructura del repositorio

```text
proyecto-inversion-py/
├── cartera.py         # Lógica de negocio: valoración, operaciones y rebalanceo
├── proyecciones.py    # Cálculo de interés compuesto iterativo y recursivo
├── main.py            # Punto de entrada CLI, menús y validación de entrada
├── test_portfolio.py  # Suite de pruebas automatizadas con assert
├── .gitignore         # Exclusión de archivos temporales (__pycache__, etc.)
└── README.md          # Documentación del proyecto
```

---

## 🧠 Conceptos de Python aplicados

Este proyecto aplica buenas prácticas de programación modular:
- **Modularización y punto de entrada**: separación clara de responsabilidades entre módulos y protección del flujo principal mediante `if __name__ == "__main__":`.
- **Paso de objetos mutables vs. inmutables**: mutación controlada de listas y diccionarios al registrar operaciones frente a funciones puras que devuelven nuevas estructuras sin efectos secundarios.
- **Iteración frente a recursividad**: implementación paralela del mismo problema matemático validando casos base y condiciones de parada.
- **Calidad y mantenibilidad**: uso de `docstrings`, anotaciones de tipo (`type hints`), manejo explícito de excepciones (`ValueError`) y pruebas con `assert`.

---

## 🚀 Requisitos y ejecución

No requiere librerías externas; funciona únicamente con la biblioteca estándar de **Python 3.10+**.

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/juan-araque/proyecto-inversion-py.git
   cd proyecto-inversion-py
   ```

2. **Ejecutar el simulador interactivo**:
   ```bash
   python main.py
   ```

3. **Ejecutar las pruebas automatizadas**:
   ```bash
   python test_portfolio.py
   ```
   Si todas las verificaciones pasan, verás por consola:
   ```text
   Todas las pruebas con assert se han superado correctamente.
   ```

---

## 💻 Ejemplo de uso

```text
=== SIMULADOR DE CARTERA Y REBALANCEO ===
1. Registrar compra o actualizar activo
2. Ver resumen y rentabilidad de la cartera
3. Calcular plan de rebalanceo con nueva aportación
4. Proyectar interés compuesto (iterativo vs. recursivo)
5. Salir
Selecciona una opción (1-5): 3
Aportación nueva a invertir: 250

--- PLAN DE REBALANCEO ---
MSCIW: Actual 800.00 (80.00%) | Obj 60.00% | Aportar: 0.00
MSCIE: Actual 200.00 (20.00%) | Obj 40.00% | Aportar: 250.00
```