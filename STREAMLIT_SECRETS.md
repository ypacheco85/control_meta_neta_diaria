# 🔐 Configuración de Streamlit Secrets

La aplicación utiliza Google Sheets para almacenar los datos. Las credenciales se configuran a través de los **Streamlit Secrets**.

## Configuración en Streamlit Cloud

Si estás usando **Streamlit Cloud**, configura los secrets en:
- Settings → Secrets → Add new secret

Agrega la siguiente estructura:

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
tu-llave-privada-completa-aqui
-----END PRIVATE KEY-----"""
client_email = "tu-email@project.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"
```

**IMPORTANTE:** 
- El `private_key` debe estar entre comillas triples `"""` para permitir saltos de línea
- Mantén todos los saltos de línea del private key
- **NUNCA** subas las credenciales a GitHub

## Configuración Local (Desarrollo)

Si estás ejecutando localmente:

1. **Crear el directorio `.streamlit`** (si no existe)
   ```bash
   mkdir -p .streamlit
   ```

2. **Crear el archivo `secrets.toml`**
   ```bash
   touch .streamlit/secrets.toml
   ```

3. **Agregar las credenciales** en formato TOML (mismo formato que arriba)

4. **Verificar que el archivo NO se suba a Git**
   - El archivo `.gitignore` ya incluye `.streamlit/` y `credential.json`
   - **NUNCA** hagas commit de archivos con credenciales

## Verificación

Una vez configurado, ejecuta la aplicación:

```bash
streamlit run driver_profit_app.py
```

Si hay errores de conexión, verifica:
1. Que los secrets están configurados correctamente (formato TOML)
2. Que el email de la cuenta de servicio tiene acceso al Google Sheet
3. Que el nombre del Google Sheet es exactamente "App_Uber_2025"
4. Que la cuenta de servicio tiene permisos de "Editor" en el Google Sheet

## Seguridad

⚠️ **IMPORTANTE:**
- Las credenciales están protegidas por `.gitignore`
- No se suben a GitHub
- Si usas Streamlit Cloud, las credenciales se almacenan de forma segura en la plataforma

