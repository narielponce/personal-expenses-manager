# Contexto del Proyecto: Gastos Personales

## Estándares de Ingeniería y UX
- **Lenguaje Visual**: Estilo "Mobile First" basado en el diseño del Home. 
    - Bordes: `rounded-4` (muy redondeados).
    - Sombras: `shadow-sm`.
    - Tipografía: Etiquetas en `tiny` (0.65rem) y negrita.
    - Componentes: Uso de "Drag Handles" visuales en tarjetas de filtro y modales.
    - Notificaciones: Uso de Toasts automáticos (2 seg) en lugar de `alert()` para confirmaciones.

## Seguridad y Sesión
- **Expiración**: Sincronizada a **5 minutos**.
- **Frontend**: Timer de inactividad que muestra un modal de "Sesión Vencida" con botón de Aceptar.
- **Backend**: `ACCESS_TOKEN_EXPIRE_MINUTES = 5`. Refresh Token de 24h.

## Inteligencia Artificial (Gemini)
- **Modelo**: Prioridad absoluta a `gemini-1.5-flash-latest` por estabilidad de cuota en el Free Tier.
- **Lógica de Fallback**: El backend lista modelos disponibles y prueba en orden (`flash-latest` -> `1.5-flash` -> `2.0-flash`) si recibe errores 429 o 404.
- **Flujo**: Tanto el Audio como la Foto envían el gasto al **Inbox** (estado `pending`) para revisión manual del usuario.

## Funcionalidades Implementadas
1. **Inbox**: Repositorio de gastos capturados por IA pendientes de confirmación.
2. **Carga Manual**: Formulario con selector de categorías en árbol (Modal) y cálculo de valor de cuota en tiempo real.
3. **Reportes**:
    - **Categorías**: Gráfico de dona (Chart.js), comparativa vs mes anterior y Drill-down jerárquico.
    - **Balance**: Comparativa Ingresos vs Gastos con gráfico de barras.
    - **Tarjetas**: Resumen de consumos y cuotas.
4. **Gestión de Datos**:
    - **Exportación**: Generación de ZIP con CSVs de todas las tablas.
    - **Reset**: Borrado total de datos y re-sembrado de categorías por defecto.
    - **Categorías por Defecto**: Estructura completa de 11 padres y subcategorías cargada automáticamente para nuevos usuarios.

## Arquitectura Técnica
- **Backend**: FastAPI, SQLAlchemy (PostgreSQL), Pydantic.
- **Frontend**: Vue 3 (Vite), Pinia, Bootstrap 5, Chart.js.
- **Ordenamiento**: Todos los listados de gastos deben estar ordenados por `date.desc()` e `id.desc()`.
