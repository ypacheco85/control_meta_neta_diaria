import streamlit as st
import datetime
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Pro Driver", page_icon="🚖", layout="wide")

# --- CONEXIÓN CON GOOGLE SHEETS ---
def get_google_sheet_data():
    """Conecta con Google y descarga los datos existentes"""
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials_dict = dict(st.secrets["gcp_service_account"])
        credentials_dict["private_key"] = credentials_dict["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Abrir hoja y pestaña
        sheet = client.open("App_Uber_2025")
        worksheet = sheet.worksheet("Driver_Finances_DB")
        return worksheet
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- BARRA LATERAL (Tus Metas) ---
with st.sidebar:
    st.header("🎯 Configuración de Meta")
    meta_diaria = st.number_input("Meta de hoy ($)", value=200, step=10)
    costo_gas_galon = st.number_input("Precio Gasolina ($/gal)", value=3.20)
    mpg_vehiculo = st.number_input("Millas por Galón (MPG)", value=25)

# --- TÍTULO Y ESTADÍSTICAS RÁPIDAS ---
st.title("🚖 Tablero de Control - Uber/Lyft")

# Intentar leer datos anteriores para mostrar acumulados
hoja = get_google_sheet_data()
if hoja:
    try:
        data = hoja.get_all_records()
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Asegurar que las columnas sean números
            df['Ingresos'] = pd.to_numeric(df['Ingresos'], errors='coerce').fillna(0)
            
            total_historico = df['Ingresos'].sum()
            registros_totales = len(df)
            
            # Mostrar métricas arriba
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Ganado (Histórico)", f"${total_historico:,.2f}")
            m2.metric("Días Trabajados", f"{registros_totales}")
            # Aquí podrías filtrar por semana actual si quisieras
        else:
            st.info("Aún no tienes datos guardados. ¡Empieza hoy!")
    except Exception as e:
        st.warning(f"No se pudieron cargar estadísticas: {e}")

st.divider()

# --- SECCIÓN DE INGRESO DE DATOS ---
st.subheader("📝 Registro del Día")

with st.form("nuevo_turno", clear_on_submit=True):
    col_fecha, col_vacio = st.columns(2)
    with col_fecha:
        fecha_hoy = st.date_input("Fecha", datetime.date.today())

    st.markdown("### 💰 Ingresos")
    c1, c2, c3 = st.columns(3)
    uber = c1.number_input("Uber ($)", 0.0, step=0.10)
    lyft = c2.number_input("Lyft ($)", 0.0, step=0.10)
    propinas = c3.number_input("Efectivo/Otros ($)", 0.0, step=0.10)

    st.markdown("### 🚗 Odómetro (Millas)")
    o1, o2 = st.columns(2)
    odo_start = o1.number_input("Inicio Turno", 0, help="Lectura al salir de casa")
    odo_end = o2.number_input("Fin Turno", 0, help="Lectura al regresar")

    st.markdown("### ⛽ Gastos")
    gastos = st.number_input("Gastos (Comida/Peajes/Gas)", 0.0, step=0.10)
    notas = st.text_area("Notas / Eventos")

    # Cálculos en tiempo real (antes de guardar)
    total_bruto = uber + lyft + propinas
    millas = odo_end - odo_start if odo_end > 0 else 0
    
    # Barra de Progreso de la Meta
    progreso = min(total_bruto / meta_diaria, 1.0) if meta_diaria > 0 else 0
    st.write(f"📊 Progreso de Meta: **${total_bruto:.2f}** / ${meta_diaria:.2f}")
    st.progress(progreso)

    if progreso >= 1.0:
        st.balloons()

    submitted = st.form_submit_button("Guardar Turno 💾", use_container_width=True)

    if submitted:
        if odo_end > 0 and odo_end < odo_start:
            st.error("⚠️ Error: El millaje final es menor que el inicial.")
        else:
            # Guardar en Google Sheets
            nueva_fila = [
                str(fecha_hoy),
                "App", # Plataforma genérica o podrías detallar
                total_bruto,
                propinas,
                gastos,
                odo_start,
                odo_end,
                millas,
                notas
            ]
            
            if hoja:
                try:
                    hoja.append_row(nueva_fila)
                    st.success("✅ ¡Datos guardados en la Nube correctamente!")
                    # Truco para recargar la página y actualizar las estadísticas de arriba
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al escribir en Google: {e}")