import streamlit as st
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas Uber/Lyft", page_icon="🚗", layout="centered")

# --- CONEXIÓN CON GOOGLE SHEETS (La parte Blindada) ---
def conectar_google_sheets():
    try:
        # Definir los permisos que necesitamos
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Cargar las credenciales desde los Secretos de Streamlit
        # Convertimos el objeto de secretos a un diccionario normal de Python
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        # Corrección de seguridad para la llave privada (a veces los espacios dan problema)
        credentials_dict["private_key"] = credentials_dict["private_key"].replace("\\n", "\n")

        # Autenticar
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Abrir el archivo y la pestaña específica
        # OJO: Asegúrate que el archivo se llame EXACTAMENTE "App_Uber_2025"
        sheet = client.open("App_Uber_2025") 
        worksheet = sheet.worksheet("Driver_Finances_DB")
        
        return worksheet
    except Exception as e:
        st.error(f"⚠️ Error conectando a Google Sheets: {e}")
        return None

# --- TÍTULO ---
st.title("🚗 Control de Ganancias")
st.write("Registra tu turno de hoy")

# --- FORMULARIO DE ENTRADA ---
with st.form("entrada_datos", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.date.today())
        odo_inicio = st.number_input("Millas Inicio (Odómetro)", min_value=0)
        odo_fin = st.number_input("Millas Final (Odómetro)", min_value=0)
    
    with col2:
        ganancia_uber = st.number_input("Ganancia Uber ($)", min_value=0.0, step=0.01)
        ganancia_lyft = st.number_input("Ganancia Lyft ($)", min_value=0.0, step=0.01)
        propinas_extra = st.number_input("Propinas/Efectivo ($)", min_value=0.0, step=0.01)
        gastos_gas = st.number_input("Gastos Gasolina/Comida ($)", min_value=0.0, step=0.01)

    notas = st.text_area("Notas del día (Opcional)")

    # Botón de Enviar
    submitted = st.form_submit_button("💾 Guardar Datos")

    if submitted:
        if odo_fin > 0 and odo_fin < odo_inicio:
            st.error("¡Error! El millaje final no puede ser menor al inicial.")
        else:
            # Cálculos automáticos
            total_ingresos = ganancia_uber + ganancia_lyft
            millas_recorridas = odo_fin - odo_inicio if odo_fin > 0 else 0
            
            # Preparar la fila para Google Sheets
            # Orden: Fecha | Plataforma (Uber+Lyft) | Ingresos Total | Propinas | Gastos | Odo_Ini | Odo_Fin | Millas | Notas
            nueva_fila = [
                str(fecha),
                "Mix Uber/Lyft", 
                total_ingresos,
                propinas_extra,
                gastos_gas,
                odo_inicio,
                odo_fin,
                millas_recorridas,
                notas
            ]
            
            # Intentar guardar
            hoja = conectar_google_sheets()
            if hoja:
                st.info("Guardando en la nube... ☁️")
                try:
                    hoja.append_row(nueva_fila)
                    st.success("✅ ¡Guardado Exitosamente en Google Sheets!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error escribiendo datos: {e}")