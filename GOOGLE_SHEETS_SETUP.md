# 📊 Configuración de Google Sheets

## Estructura Requerida

La aplicación requiere un archivo de Google Sheets llamado **"App_Uber_2025"** con dos hojas:

### Hoja 1: "Config"
Esta hoja almacena la configuración del vehículo.

**Estructura:**
```
A1: MPG
B1: Gas Price
C1: Meta Neta Objetivo

A2: 35.0
B2: 3.10
C2: 200.0
```

### Hoja 2: "Driver_Finances_DB"
Esta hoja almacena todos los registros diarios.

**Encabezados (Fila 1):**
| Columna | Nombre | Descripción |
|---------|--------|-------------|
| A | Fecha | Fecha del registro (YYYY-MM-DD) |
| B | Uber Earnings | Ganancia de Uber |
| C | Lyft Earnings | Ganancia de Lyft |
| D | Cash Tips | Propinas en efectivo |
| E | Additional Income | Ingresos adicionales (JSON) |
| F | Odo Start | Odómetro inicial |
| G | Odo End | Odómetro final |
| H | Miles Driven | Millas recorridas |
| I | Gallons Used | Galones usados |
| J | Fuel Cost | Costo de combustible |
| K | Food Cost | Costo de comida |
| L | Misc Cost | Gastos varios |
| M | Additional Expenses | Gastos adicionales (JSON) |
| N | Wear And Tear | Reserva por desgaste |
| O | Total Gross | Ingreso bruto total |
| P | Total Expenses | Gastos totales |
| Q | Net Profit | Ganancia neta |
| R | Meta Neta Objetivo | Meta del día |
| S | Expense Ratio | Ratio de gastos (%) |

## Pasos para Configurar

1. **Crear el archivo de Google Sheets**
   - Ve a [Google Sheets](https://sheets.google.com)
   - Crea un nuevo archivo
   - Nómbralo exactamente: **"App_Uber_2025"**

2. **Crear la hoja "Config"**
   - Haz clic en el botón "+" para agregar una nueva hoja
   - Renómbrala a "Config"
   - En la fila 1, agrega los encabezados: `MPG`, `Gas Price`, `Meta Neta Objetivo`
   - En la fila 2, agrega valores por defecto: `35.0`, `3.10`, `200.0`

3. **Crear la hoja "Driver_Finances_DB"**
   - Agrega otra hoja
   - Renómbrala a "Driver_Finances_DB"
   - En la fila 1, agrega todos los encabezados listados arriba

4. **Configurar Permisos**
   - Comparte el archivo con el email de la cuenta de servicio
   - El email está en tu archivo `credential.json` (campo `client_email`)
   - Dale permisos de "Editor"

5. **Configurar Streamlit Secrets**
   - Crea un archivo `.streamlit/secrets.toml` en tu proyecto
   - Copia el contenido de `credential.json` en formato TOML:

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "tu-email@project.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"
```

## Notas Importantes

- Los encabezados deben estar exactamente como se muestran arriba
- La primera fila siempre debe contener los encabezados
- Los datos comienzan en la fila 2
- Los ingresos y gastos adicionales se guardan como JSON en las celdas
- La aplicación creará automáticamente los encabezados si no existen

