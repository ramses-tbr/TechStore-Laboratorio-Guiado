# TechStore - Actividad Fundamental 4 Laboratorio Guiado
# Equipo: 2
| Matrícula | Nombre |
|-----------|--------|
| 2049234 | Basurto Rivera Ramsés Tenosh |
| 2050864 | Cerda Herrera Juan Kristof |
| 2066053 | Esparza Torres Carlos Arturo |

Sistema que implementa reglas de negocio de TechStore, usando Patron Specification para reglas complejas, una Máquina de Estados para el ciclo de vida de las ordenes, además utilizando FastAPI y pytest.

## Instalación y Ejecución
1. **Clonar el repositorio:**
   ```bash
   git clone <https://github.com/ramses-tbr/TechStore-Laboratorio-Guiado>
   cd techstore
2. **Crear y activar entorno virtual**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  *(**macOS**)
    ```
    .venv\Scripts\activate  *(**Windows**)
    ```
3. **Instalar dependencias**
    ```bash
    pip install fastapi uvicorn pytest httpx
4. **Ejecutar el servidor local de la API (FastAPI)**
    ```bash
    uvicorn app.api:app --reload
    En el navegador: http://127.0.0.1:8000/docs
    Contrato OpenAPI: http://127.0.0.1:8000/openapi.json
5. **Pruebas automatizadas (pytest)**
    ```bash
    PYTHONPATH=. .venv/bin/pytest -s  *(**macOS**)
    ```
    set PYTHONPATH=. && .venv\Scripts\pytest -s  *(**Windows**)
    ```

## Reglas
Patrón Specification (app/specifications.py): Permite componer reglas de descuento de forma flexible utilizando operadores lógicos sobrecargados (&, |, ~). Se evalúan condiciones sobre el monto mínimo, estatus VIP del cliente, cantidad mínima de unidades (OrderItem) y ausencia de promociones activas.

Máquina de Estados (app/domain.py): Controla las transiciones válidas de los pedidos (DRAFT ➔ CONFIRMED ➔ SHIPPED ➔ DELIVERED o CANCELLED/RETURNED), lanzando excepciones de dominio cuando se intenta una operación inválida.

## Endpoints
GET /orders/{order_id}: Consulta la información detallada de un pedido específico.
POST /orders/{order_id}/confirm: Transiciona un pedido de estado DRAFT a CONFIRMED, validando items y cliente activo.
POST /orders/{order_id}/ship: Registra el envío de un pedido confirmado añadiendo un número de guía (tracking_number).
POST /orders/{order_id}/cancel: Cancela un pedido existente bajo las restricciones del ciclo de vida.