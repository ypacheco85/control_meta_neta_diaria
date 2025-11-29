# 🚗 Control de Meta Neta Diaria - Uber/Lyft

Aplicación web para el control financiero diario de conductores de Uber/Lyft. Permite registrar ingresos, gastos operativos, calcular ganancias netas y hacer seguimiento de metas diarias, semanales y mensuales.

## 📋 Características

### ✨ Funcionalidades Principales

- **Registro Diario Completo**
  - Ingresos de Uber, Lyft y propinas
  - Ingresos adicionales personalizados
  - Cálculo automático de gastos de combustible basado en odómetro
  - Gastos operativos (comida, peajes, etc.)
  - Gastos adicionales personalizados
  - Cálculo de reserva por desgaste del vehículo

- **Gestión de Fechas**
  - Selección manual de fecha para registrar días anteriores
  - Modificación de registros existentes
  - Carga automática del odómetro inicial desde el último registro

- **Análisis y Estadísticas**
  - Vista diaria con formulario completo
  - Vista semanal con resumen de últimos 7 días
  - Vista mensual con resumen de últimos 30 días
  - Comparativa con metas semanales y mensuales
  - Historial completo de registros
  - Estadísticas agregadas

- **Indicadores de Salud Financiera**
  - Semáforo de gastos (Verde/Amarillo/Rojo)
  - Porcentaje de gastos sobre ingresos
  - Barra de progreso hacia la meta diaria
  - Alertas visuales cuando se alcanza la meta

## 🚀 Instalación

### Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/control_financiero.git
   cd control_financiero
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   streamlit run driver_profit_app.py
   ```

4. **Abrir en el navegador**
   - La aplicación se abrirá automáticamente en `http://localhost:8501`
   - Si no se abre automáticamente, accede manualmente a esa dirección

## 📁 Estructura del Proyecto

```
control_financiero/
├── driver_profit_app.py    # Aplicación principal Streamlit
├── database.py              # Módulo de base de datos SQLite
├── index.html              # Versión web estática (HTML/CSS/JS)
├── styles.css              # Estilos CSS para versión web
├── script.js               # JavaScript para versión web
├── requirements.txt        # Dependencias de Python
├── README.md              # Este archivo
└── .gitignore             # Archivos a ignorar en Git
```

## 💾 Base de Datos

La aplicación utiliza SQLite para almacenar los registros. La base de datos se crea automáticamente al ejecutar la aplicación por primera vez.

### Estructura de la Base de Datos

- **daily_records**: Almacena todos los registros diarios
- **vehicle_config**: Almacena la configuración del vehículo (MPG, precio gasolina, meta diaria)

### Datos Almacenados

- Ingresos (Uber, Lyft, propinas, ingresos adicionales)
- Gastos (combustible, comida, peajes, gastos adicionales)
- Odómetro (inicial y final)
- Millas recorridas y galones usados
- Ganancia neta y ratio de gastos
- Fecha del registro

## 🎯 Uso

### Registro Diario

1. Selecciona la fecha del registro (puede ser hoy o un día anterior)
2. Completa los ingresos del día
3. Agrega ingresos adicionales si los hay
4. Ingresa el odómetro inicial y final
5. Completa los gastos operativos
6. Agrega gastos adicionales si los hay
7. Revisa el resultado final y guarda el registro

### Vista Semanal

1. Selecciona "📆 Semanal" en el menú lateral
2. Verás el resumen de los últimos 7 días
3. Compara tu rendimiento con la meta semanal (meta diaria × 7)
4. Revisa los registros individuales de la semana

### Vista Mensual

1. Selecciona "📅 Mensual" en el menú lateral
2. Verás el resumen de los últimos 30 días
3. Compara tu rendimiento con la meta mensual (meta diaria × 30)
4. Revisa todos los registros del mes

## ⚙️ Configuración

### Configuración del Vehículo

En el sidebar puedes configurar:
- **MPG (Millas por Galón)**: Consumo promedio de tu vehículo
- **Precio de Gasolina**: Precio por galón
- **Meta Neta Diaria**: Meta de ganancia neta que deseas alcanzar cada día

Estos valores se guardan automáticamente y se usan para todos los cálculos.

## 📊 Cálculos Automáticos

- **Ingreso Bruto Total**: Suma de todos los ingresos
- **Costo de Combustible**: Basado en millas recorridas y MPG
- **Gastos Totales**: Combustible + comida + peajes + gastos adicionales
- **Ganancia Neta**: Ingreso bruto - gastos totales
- **Ratio de Gastos**: Porcentaje de gastos sobre ingresos
- **Reserva por Desgaste**: $0.10 por milla (estimación)

## 🎨 Versión Web Estática

El proyecto incluye también una versión web estática (`index.html`) que funciona sin servidor:
- Abre `index.html` directamente en tu navegador
- Utiliza IndexedDB (base de datos del navegador) para almacenar datos
- Funciona completamente offline

## 🔧 Tecnologías Utilizadas

- **Python 3.9+**
- **Streamlit**: Framework para aplicaciones web en Python
- **SQLite**: Base de datos relacional
- **HTML/CSS/JavaScript**: Versión web estática
- **IndexedDB**: Base de datos del navegador para versión web

## 📝 Notas

- La base de datos se crea automáticamente en el directorio del proyecto
- Los datos se almacenan localmente en tu máquina
- Puedes modificar registros de cualquier fecha
- El odómetro inicial se carga automáticamente desde el último registro

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👤 Autor

Creado para ayudar a conductores de Uber/Lyft a mantener un mejor control de sus finanzas diarias.

## 🙏 Agradecimientos

- Streamlit por el excelente framework
- La comunidad de Python por las herramientas disponibles

---

**¡Buena suerte con tus metas financieras! 🚗💰**

