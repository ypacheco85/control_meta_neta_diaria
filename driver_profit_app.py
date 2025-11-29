import streamlit as st
import database as db
from datetime import datetime, timedelta
import json

# Configuración de la página
st.set_page_config(page_title="Tablero de Rentabilidad - Uber/Lyft", page_icon="🚗", layout="centered")

# Título y Estilo
st.title("🚗 Control de Meta Neta Diaria")
st.markdown("---")

# Obtener view_option del sidebar primero (se define más abajo, pero necesitamos verificar aquí)
# Usar session_state para mantener la selección
if 'view_option' not in st.session_state:
    st.session_state.view_option = "📅 Diario"

# Cargar configuración del vehículo desde Google Sheets
try:
    vehicle_config = db.get_vehicle_config()
except Exception as e:
    vehicle_config = {'mpg': 35.0, 'gas_price': 3.10, 'meta_neta_objetivo': 200.0}
    # Si hay error, se mostrará en get_connection()

# --- BARRA LATERAL: CONFIGURACIÓN DEL VEHÍCULO ---
st.sidebar.header("⚙️ Configuración del Auto")
st.sidebar.info("Ajusta esto según tu Toyota Highlander 2025")

# Consumo Promedio (MPG - Millas por Galón)
mpg = st.sidebar.number_input("Consumo Promedio (MPG)", value=float(vehicle_config['mpg']), step=0.1, help="Millas por galón de tu vehículo")

# Precio de la Gasolina
gas_price = st.sidebar.number_input("Precio Gasolina ($/galón)", value=float(vehicle_config['gas_price']), step=0.01)

# Meta Neta Deseada
meta_neta_objetivo = st.sidebar.number_input("Meta Neta Diaria ($)", value=float(vehicle_config['meta_neta_objetivo']), step=10.0)

# Guardar configuración cuando cambie
if mpg != vehicle_config['mpg'] or gas_price != vehicle_config['gas_price'] or meta_neta_objetivo != vehicle_config['meta_neta_objetivo']:
    db.update_vehicle_config(mpg, gas_price, meta_neta_objetivo)

# --- SELECTOR DE FECHA ---
st.sidebar.markdown("---")
st.sidebar.header("📅 Seleccionar Fecha")
selected_date = st.sidebar.date_input(
    "Fecha del registro:",
    value=datetime.now().date(),
    max_value=datetime.now().date(),
    help="Selecciona la fecha del registro que deseas ver o editar"
)

# Cargar registro de la fecha seleccionada
selected_date_str = selected_date.isoformat()
try:
    selected_record = db.get_record_by_date(selected_date_str)
except:
    selected_record = None

# Mostrar información del registro seleccionado
if selected_record:
    if selected_date == datetime.now().date():
        st.sidebar.success(f"📅 Registro de hoy cargado")
    else:
        st.sidebar.info(f"📅 Registro del {selected_date.strftime('%d/%m/%Y')} cargado")
    
    col_del1, col_del2 = st.sidebar.columns(2)
    with col_del1:
        if st.button("🔄 Limpiar registro", key="clear_record"):
            db.delete_record(selected_date_str)
            st.rerun()
    with col_del2:
        if st.button("📋 Cargar en formulario", key="load_record"):
            # Forzar recarga de datos
            if 'last_loaded_date' in st.session_state:
                del st.session_state.last_loaded_date
            st.rerun()
else:
    if selected_date == datetime.now().date():
        st.sidebar.info("📝 No hay registro para hoy. Completa el formulario y guarda.")
    else:
        st.sidebar.info(f"📝 No hay registro para el {selected_date.strftime('%d/%m/%Y')}. Completa el formulario y guarda.")

# --- MENÚ LATERAL: NAVEGACIÓN ---
st.sidebar.markdown("---")
st.sidebar.header("📊 Navegación")

# Selector de vista (mover al inicio para controlar qué se muestra)
view_option = st.sidebar.radio(
    "Selecciona la vista:",
    ["📅 Diario", "📆 Semanal", "📅 Mensual"],
    index=0
)
st.session_state.view_option = view_option

# Mostrar acumulados según la selección
if view_option == "📆 Semanal":
    st.sidebar.markdown("### Seleccionar Semana")
    
    # Calcular semanas disponibles (últimas 12 semanas)
    today = datetime.now().date()
    current_week_start, _ = db.get_week_start_end(today)
    
    # Generar lista de semanas (semana actual y 11 anteriores)
    weeks_list = []
    for i in range(12):
        week_start = current_week_start - timedelta(days=7 * i)
        week_end = week_start + timedelta(days=6)
        week_label = f"Semana {week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}"
        if i == 0:
            week_label = f"📅 {week_label} (Actual)"
        weeks_list.append((week_start, week_label))
    
    # Selector de semana
    week_options = [label for _, label in weeks_list]
    selected_week_idx = st.sidebar.selectbox(
        "Semana:",
        range(len(week_options)),
        format_func=lambda x: week_options[x],
        key="week_selector"
    )
    selected_week_start = weeks_list[selected_week_idx][0]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Resumen Semanal")
    try:
        weekly = db.get_weekly_summary(meta_neta_objetivo, selected_week_start)
        
        # Mostrar rango de fechas
        st.sidebar.caption(f"📅 {weekly['week_start'].strftime('%d/%m')} - {weekly['week_end'].strftime('%d/%m/%Y')}")
        
        st.sidebar.metric("Días registrados", f"{weekly['days']}/7")
        st.sidebar.metric("💰 Ingresos Totales", f"${weekly['total_income']:.2f}")
        st.sidebar.metric("💸 Gastos Totales", f"${weekly['total_expenses']:.2f}")
        st.sidebar.metric("🏆 Ganancia Neta", f"${weekly['total_profit']:.2f}")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Meta Semanal")
        st.sidebar.metric("Meta (7 días)", f"${weekly['meta_semanal']:.2f}")
        
        diferencia = weekly['diferencia_meta']
        if diferencia >= 0:
            st.sidebar.success(f"✅ +${diferencia:.2f} sobre la meta")
        else:
            st.sidebar.error(f"❌ ${abs(diferencia):.2f} bajo la meta")
        
        st.sidebar.progress(min(weekly['porcentaje_meta'] / 100, 1.0))
        st.sidebar.caption(f"Progreso: {weekly['porcentaje_meta']:.1f}%")
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota exceeded" in error_str:
            st.sidebar.error("⚠️ Límite de solicitudes excedido")
            st.sidebar.warning("Espera 1-2 minutos y recarga la página")
            if st.sidebar.button("🔄 Limpiar caché y reintentar", key="clear_cache_weekly"):
                st.cache_data.clear()
                st.rerun()
        else:
            st.sidebar.error(f"Error cargando datos semanales: {e}")

elif view_option == "📅 Mensual":
    st.sidebar.markdown("### Seleccionar Mes")
    
    # Calcular mes actual
    today = datetime.now().date()
    current_year = today.year
    current_month = today.month
    
    # Selector de año y mes
    years_list = list(range(current_year - 1, current_year + 1))
    months_list = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]
    
    selected_year = st.sidebar.selectbox("Año:", years_list, index=len(years_list)-1, key="year_selector")
    selected_month = st.sidebar.selectbox(
        "Mes:",
        range(1, 13),
        format_func=lambda x: months_list[x-1][1],
        index=current_month - 1 if selected_year == current_year else 0,
        key="month_selector"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Resumen Mensual")
    try:
        monthly = db.get_monthly_summary(meta_neta_objetivo, selected_year, selected_month)
        
        # Mostrar rango de fechas
        month_name = months_list[selected_month - 1][1]
        st.sidebar.caption(f"📅 {month_name} {selected_year}")
        
        st.sidebar.metric("Días registrados", f"{monthly['days']}/{monthly['days_in_month']}")
        st.sidebar.metric("💰 Ingresos Totales", f"${monthly['total_income']:.2f}")
        st.sidebar.metric("💸 Gastos Totales", f"${monthly['total_expenses']:.2f}")
        st.sidebar.metric("🏆 Ganancia Neta", f"${monthly['total_profit']:.2f}")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Meta Mensual")
        st.sidebar.metric(f"Meta ({monthly['days_in_month']} días)", f"${monthly['meta_mensual']:.2f}")
        
        diferencia = monthly['diferencia_meta']
        if diferencia >= 0:
            st.sidebar.success(f"✅ +${diferencia:.2f} sobre la meta")
        else:
            st.sidebar.error(f"❌ ${abs(diferencia):.2f} bajo la meta")
        
        st.sidebar.progress(min(monthly['porcentaje_meta'] / 100, 1.0))
        st.sidebar.caption(f"Progreso: {monthly['porcentaje_meta']:.1f}%")
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota exceeded" in error_str:
            st.sidebar.error("⚠️ Límite de solicitudes excedido")
            st.sidebar.warning("Espera 1-2 minutos y recarga la página")
            if st.sidebar.button("🔄 Limpiar caché y reintentar", key="clear_cache_monthly"):
                st.cache_data.clear()
                st.rerun()
        else:
            st.sidebar.error(f"Error cargando datos mensuales: {e}")

# Mostrar formulario solo si está en modo Diario
if view_option == "📅 Diario":
    # --- SECCIÓN 1: INGRESOS ---
    st.header("1. Ingresos Brutos")
    col1, col2, col3 = st.columns(3)
    with col1:
        uber_earnings = st.number_input("Ganancia Uber ($)", min_value=0.0, step=1.0, value=float(selected_record['uber_earnings']) if selected_record else 0.0)
    with col2:
        lyft_earnings = st.number_input("Ganancia Lyft ($)", min_value=0.0, step=1.0, value=float(selected_record['lyft_earnings']) if selected_record else 0.0)
    with col3:
        cash_tips = st.number_input("Efectivo/Propina ($)", min_value=0.0, step=1.0, value=float(selected_record['cash_tips']) if selected_record else 0.0)

    # Inicializar lista de ingresos adicionales en session_state
    if 'additional_income' not in st.session_state:
        st.session_state.additional_income = []

    # Usar la fecha seleccionada como clave para saber cuándo recargar
    if 'last_loaded_date' not in st.session_state or st.session_state.last_loaded_date != selected_date_str:
        # Cargar ingresos adicionales desde el registro seleccionado si existe
        if selected_record and selected_record.get('additional_income'):
            if isinstance(selected_record['additional_income'], list):
                st.session_state.additional_income = selected_record['additional_income']
            else:
                try:
                    st.session_state.additional_income = json.loads(selected_record['additional_income'])
                except:
                    st.session_state.additional_income = []
        else:
            st.session_state.additional_income = []
        st.session_state.last_loaded_date = selected_date_str

    # Sección para agregar ingresos adicionales
    st.subheader("➕ Ingresos Adicionales")
    st.caption("Agrega otras fuentes de ingresos del día")

    # Mostrar ingresos adicionales existentes
    if 'additional_income' in st.session_state and st.session_state.additional_income:
        st.write("**Ingresos agregados:**")
        for idx, income in enumerate(st.session_state.additional_income):
            col_name, col_amount, col_delete = st.columns([3, 1, 1])
            with col_name:
                st.write(f"💰 {income['name']}")
            with col_amount:
                st.write(f"${income['amount']:.2f}")
            with col_delete:
                if st.button("🗑️", key=f"delete_income_{idx}"):
                    st.session_state.additional_income.pop(idx)
                    st.rerun()

    # Formulario para agregar nuevo ingreso
    with st.expander("➕ Agregar Nuevo Ingreso"):
        new_income_col1, new_income_col2 = st.columns([2, 1])
        with new_income_col1:
            new_income_name = st.text_input("Fuente de ingreso", key="new_income_name", placeholder="Ej: Propinas adicionales, Bonos, etc.")
        with new_income_col2:
            new_income_amount = st.number_input("Cantidad ($)", min_value=0.0, step=1.0, key="new_income_amount", value=0.0)
        
        if st.button("Agregar Ingreso", type="secondary", key="add_income_btn"):
            if new_income_name and new_income_amount > 0:
                st.session_state.additional_income.append({
                    'name': new_income_name,
                    'amount': float(new_income_amount)
                })
                st.rerun()
            elif new_income_name == "":
                st.warning("⚠️ Ingresa una descripción para el ingreso")
            elif new_income_amount <= 0:
                st.warning("⚠️ Ingresa una cantidad mayor a 0")

    # Calcular total de ingresos adicionales
    additional_income_total = sum(inc['amount'] for inc in st.session_state.get('additional_income', []))
    if additional_income_total > 0:
        st.info(f"💰 **Total de ingresos adicionales:** ${additional_income_total:.2f}")

    # Calcular ingreso bruto total
    total_gross = uber_earnings + lyft_earnings + cash_tips + additional_income_total
    st.metric(label="💰 Ingreso Bruto Total", value=f"${total_gross:.2f}")

    # --- SECCIÓN 2: COSTO DE COMBUSTIBLE (ODÓMETRO) ---
    st.markdown("---")
    st.header("2. Cálculo de Combustible")

    # Obtener el valor inicial del odómetro
    # Si hay un registro para la fecha seleccionada, usar ese valor
    # Si no hay registro, usar el valor final del último registro guardado
    if selected_record:
        odo_start_value = int(selected_record['odo_start']) if selected_record.get('odo_start') else 0
        odo_end_value = int(selected_record['odo_end']) if selected_record.get('odo_end') else 0
    else:
        # No hay registro para esta fecha, obtener el último registro
        try:
            last_record = db.get_last_record()
            if last_record and last_record.get('odo_end'):
                # Usar el odómetro final del último registro como inicial del nuevo
                odo_start_value = int(last_record['odo_end'])
                odo_end_value = 0
            else:
                odo_start_value = 0
                odo_end_value = 0
        except:
            odo_start_value = 0
            odo_end_value = 0

    odo_col1, odo_col2 = st.columns(2)
    with odo_col1:
        odo_start = st.number_input("Odómetro INICIAL", min_value=0, value=odo_start_value, step=1)
    with odo_col2:
        odo_end = st.number_input("Odómetro FINAL (o Actual)", min_value=0, value=odo_end_value, step=1)

    # Lógica de cálculo de millas
    miles_driven = 0.0
    if odo_end > odo_start and odo_start > 0:
        miles_driven = odo_end - odo_start
    elif odo_end > 0 and odo_start == 0:
        st.warning("⚠️ Ingresa el odómetro inicial para calcular el gasto de gasolina.")

    # Cálculo de Costo de Gasolina
    gallons_used = miles_driven / mpg if mpg > 0 else 0
    fuel_cost = gallons_used * gas_price

    # Mostrar métricas de manejo
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Millas Recorridas", f"{miles_driven:.1f} mi")
    m_col2.metric("Galones Estimados", f"{gallons_used:.2f} gal")
    m_col3.metric("⛽ Costo Combustible", f"${fuel_cost:.2f}", delta_color="inverse")

    # --- SECCIÓN 3: OTROS GASTOS OPERATIVOS ---
    st.markdown("---")
    st.header("3. Otros Gastos Operativos")

    # Gastos básicos
    food_cost = st.number_input("Comida / Café ($)", min_value=0.0, step=1.0, value=float(selected_record['food_cost']) if selected_record else 0.0)
    misc_cost = st.number_input("Peajes / Lavado / Otros ($)", min_value=0.0, step=1.0, value=float(selected_record['misc_cost']) if selected_record else 0.0)

    # Inicializar lista de gastos adicionales en session_state
    # Usar la fecha seleccionada como clave para saber cuándo recargar
    if 'additional_expenses' not in st.session_state:
        st.session_state.additional_expenses = []

    if 'last_loaded_date' not in st.session_state or st.session_state.last_loaded_date != selected_date_str:
        # Cargar gastos adicionales desde el registro seleccionado si existe
        if selected_record and selected_record.get('additional_expenses'):
            if isinstance(selected_record['additional_expenses'], list):
                st.session_state.additional_expenses = selected_record['additional_expenses']
            else:
                try:
                    st.session_state.additional_expenses = json.loads(selected_record['additional_expenses'])
                except:
                    st.session_state.additional_expenses = []
        else:
            st.session_state.additional_expenses = []

    # Sección para agregar gastos adicionales
    st.subheader("➕ Gastos Adicionales")
    st.caption("Agrega otros gastos operativos del día")

    # Mostrar gastos adicionales existentes
    if 'additional_expenses' in st.session_state and st.session_state.additional_expenses:
        st.write("**Gastos agregados:**")
        for idx, expense in enumerate(st.session_state.additional_expenses):
            col_name, col_amount, col_delete = st.columns([3, 1, 1])
            with col_name:
                st.write(f"📝 {expense['name']}")
            with col_amount:
                st.write(f"${expense['amount']:.2f}")
            with col_delete:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.additional_expenses.pop(idx)
                    st.rerun()

    # Formulario para agregar nuevo gasto
    with st.expander("➕ Agregar Nuevo Gasto"):
        new_expense_col1, new_expense_col2 = st.columns([2, 1])
        with new_expense_col1:
            new_expense_name = st.text_input("Descripción del gasto", key="new_expense_name", placeholder="Ej: Estacionamiento, Reparación, etc.")
        with new_expense_col2:
            new_expense_amount = st.number_input("Cantidad ($)", min_value=0.0, step=1.0, key="new_expense_amount", value=0.0)
        
        if st.button("Agregar Gasto", type="secondary"):
            if new_expense_name and new_expense_amount > 0:
                st.session_state.additional_expenses.append({
                    'name': new_expense_name,
                    'amount': float(new_expense_amount)
                })
                st.rerun()
            elif new_expense_name == "":
                st.warning("⚠️ Ingresa una descripción para el gasto")
            elif new_expense_amount <= 0:
                st.warning("⚠️ Ingresa una cantidad mayor a 0")

    # Calcular total de gastos adicionales
    additional_expenses_total = sum(exp['amount'] for exp in st.session_state.get('additional_expenses', []))
    if additional_expenses_total > 0:
        st.info(f"💰 **Total de gastos adicionales:** ${additional_expenses_total:.2f}")

    # Reserva por Desgaste (Opcional - Depreciación, llantas, aceite)
    # Un estándar prudente es $0.10 por milla para mantenimiento futuro
    wear_and_tear = miles_driven * 0.10
    st.caption(f"Reserva estimada por desgaste ($0.10/milla): ${wear_and_tear:.2f} (No se descuenta del efectivo hoy, pero tenlo en cuenta)")

    # --- ANÁLISIS FINAL Y SALUD FINANCIERA ---
    st.markdown("---")
    st.header("📊 Resultado Final")

    # Calcular total de gastos (incluyendo gastos adicionales)
    additional_expenses_total = sum(exp['amount'] for exp in st.session_state.get('additional_expenses', []))
    total_expenses = fuel_cost + food_cost + misc_cost + additional_expenses_total
    net_profit = total_gross - total_expenses

    # Indicador de Salud del Gasto
    # Calculamos qué porcentaje del ingreso bruto se fue en gastos
    expense_ratio = 0.0
    if total_gross > 0:
        expense_ratio = (total_expenses / total_gross) * 100

    # Lógica del Semáforo (Verde, Amarillo, Rojo)
    health_color = "green"
    health_msg = "✅ SALUDABLE: Tus gastos están bajo control."

    if total_gross == 0:
        health_msg = "Esperando ingresos..."
        health_color = "gray"
    elif expense_ratio < 20:
        health_color = "green" # Gasto bajo (Excelente)
        health_msg = f"✅ EXCELENTE: Gastos operativos al {expense_ratio:.1f}% (Muy Rentable)"
    elif 20 <= expense_ratio <= 35:
        health_color = "orange" # Gasto medio (Cuidado)
        health_msg = f"⚠️ ATENCIÓN: Gastos operativos al {expense_ratio:.1f}% (Vigila el consumo)"
    else:
        health_color = "red" # Gasto alto (Peligro)
        health_msg = f"🛑 ALERTA: Gastos operativos al {expense_ratio:.1f}% (Estás gastando demasiado)"

    # Mostrar Alertas de Salud
    if total_gross > 0:
        if health_color == "green":
            st.success(health_msg)
        elif health_color == "orange":
            st.warning(health_msg)
        else:
            st.error(health_msg)

    # Tarjetas Grandes de Resultado
    res_col1, res_col2 = st.columns(2)
    fecha_label = "Hoy" if selected_date == datetime.now().date() else selected_date.strftime('%d/%m/%Y')
    res_col1.metric(label=f"💸 Gastos Totales ({fecha_label})", value=f"${total_expenses:.2f}", delta=f"-{expense_ratio:.1f}% del ingreso")
    res_col2.metric(label="🏆 GANANCIA NETA (Bolsillo)", value=f"${net_profit:.2f}", delta=f"${net_profit - meta_neta_objetivo:.2f} vs Meta")

    # Barra de Progreso hacia la Meta
    if meta_neta_objetivo > 0:
        progress = min(net_profit / meta_neta_objetivo, 1.0)
        if progress < 0: progress = 0
        st.progress(progress)
        st.caption(f"Progreso hacia la meta de ${meta_neta_objetivo} Netos: {progress*100:.1f}%")

    if net_profit >= meta_neta_objetivo:
        st.balloons()
        st.success("🎉 ¡FELICIDADES! HAS LOGRADO TU META NETA DE HOY.")

    # --- GUARDAR EN BASE DE DATOS ---
    st.markdown("---")
    fecha_label_btn = "Hoy" if selected_date == datetime.now().date() else selected_date.strftime('%d/%m/%Y')
    col_save1, col_save2, col_save3 = st.columns([1, 1, 1])
    with col_save2:
        if st.button(f"💾 Guardar Registro del {fecha_label_btn}", type="primary", use_container_width=True):
            record_data = {
                'mpg': mpg,
                'gas_price': gas_price,
                'meta_neta_objetivo': meta_neta_objetivo,
                'uber_earnings': uber_earnings,
                'lyft_earnings': lyft_earnings,
                'cash_tips': cash_tips,
                'additional_income': st.session_state.get('additional_income', []),
                'odo_start': odo_start,
                'odo_end': odo_end,
                'miles_driven': miles_driven,
                'gallons_used': gallons_used,
                'fuel_cost': fuel_cost,
                'food_cost': food_cost,
                'misc_cost': misc_cost,
                'additional_expenses': st.session_state.get('additional_expenses', []),
                'wear_and_tear': wear_and_tear,
                'total_gross': total_gross,
                'total_expenses': total_expenses,
                'net_profit': net_profit,
                'expense_ratio': expense_ratio
            }
            if db.save_daily_record(record_data, selected_date_str):
                st.success(f"✅ Registro del {fecha_label_btn} guardado exitosamente en Google Sheets!")
                st.rerun()
            else:
                st.error("❌ Error al guardar el registro")

    # --- HISTORIAL Y ESTADÍSTICAS (solo visible en modo Diario) ---
    st.markdown("---")
    st.header("📈 Historial y Estadísticas")

    tab1, tab2 = st.tabs(["📊 Estadísticas", "📅 Historial"])

    with tab1:
        try:
            stats = db.get_statistics()
            if stats['total_days'] > 0:
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                stat_col1.metric("Días Registrados", f"{stats['total_days']}")
                stat_col2.metric("Ingreso Total", f"${stats['total_income']:.2f}")
                stat_col3.metric("Gastos Total", f"${stats['total_expenses']:.2f}")
                stat_col4.metric("Ganancia Total", f"${stats['total_profit']:.2f}")
                
                stat_col5, stat_col6, stat_col7 = st.columns(3)
                stat_col5.metric("Ganancia Promedio/Día", f"${stats['avg_daily_profit']:.2f}")
                stat_col6.metric("Millas Totales", f"{stats['total_miles']:.1f} mi")
                stat_col7.metric("Combustible Total", f"${stats['total_fuel_cost']:.2f}")
            else:
                st.info("No hay registros aún. Guarda tu primer registro para ver estadísticas.")
        except Exception as e:
            st.error(f"Error cargando estadísticas: {e}")

    with tab2:
        try:
            records = db.get_all_records(limit=30)
            if records:
                st.subheader("Últimos 30 Registros")
                for record in records:
                    with st.expander(f"📅 {record.get('date', 'Sin fecha')} - Ganancia Neta: ${float(record.get('net_profit', 0)):.2f}"):
                        col_h1, col_h2, col_h3 = st.columns(3)
                        col_h1.metric("Ingreso Bruto", f"${float(record.get('total_gross', 0)):.2f}")
                        col_h2.metric("Gastos", f"${float(record.get('total_expenses', 0)):.2f}")
                        col_h3.metric("Ganancia Neta", f"${float(record.get('net_profit', 0)):.2f}")
                        
                        col_h4, col_h5 = st.columns(2)
                        col_h4.write(f"**Millas:** {float(record.get('miles_driven', 0)):.1f} mi")
                        col_h5.write(f"**Combustible:** ${float(record.get('fuel_cost', 0)):.2f}")
                        
                        if st.button(f"🗑️ Eliminar", key=f"delete_{record.get('date', '')}"):
                            db.delete_record(record.get('date', ''))
                            st.rerun()
            else:
                st.info("No hay registros en el historial.")
        except Exception as e:
            st.error(f"Error cargando historial: {e}")

# Mostrar sección de historial y estadísticas para Semanal y Mensual
elif view_option in ["📆 Semanal", "📅 Mensual"]:
    st.header("📈 Historial y Estadísticas")
    
    if view_option == "📆 Semanal":
        # Obtener la semana seleccionada del sidebar
        today = datetime.now().date()
        current_week_start, _ = db.get_week_start_end(today)
        
        # Generar lista de semanas (mismo cálculo que en sidebar)
        weeks_list = []
        for i in range(12):
            week_start = current_week_start - timedelta(days=7 * i)
            weeks_list.append(week_start)
        
        # Obtener índice seleccionado (si existe en session_state, sino usar 0)
        selected_week_idx = st.session_state.get('week_selector', 0)
        if selected_week_idx >= len(weeks_list):
            selected_week_idx = 0
        selected_week_start = weeks_list[selected_week_idx]
        
        st.subheader(f"📆 Resumen Semanal")
        st.caption(f"Semana del {selected_week_start.strftime('%d/%m/%Y')} al {(selected_week_start + timedelta(days=6)).strftime('%d/%m/%Y')}")
        
        try:
            weekly = db.get_weekly_summary(meta_neta_objetivo, selected_week_start)
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Días registrados", f"{weekly['days']}/7")
            col2.metric("💰 Ingresos Totales", f"${weekly['total_income']:.2f}")
            col3.metric("💸 Gastos Totales", f"${weekly['total_expenses']:.2f}")
            col4.metric("🏆 Ganancia Neta", f"${weekly['total_profit']:.2f}")
            
            st.markdown("---")
            
            # Meta semanal
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.metric("Meta Semanal (7 días)", f"${weekly['meta_semanal']:.2f}")
            with col_meta2:
                diferencia = weekly['diferencia_meta']
                if diferencia >= 0:
                    st.metric("Diferencia vs Meta", f"+${diferencia:.2f}", delta="✅ Sobre la meta")
                else:
                    st.metric("Diferencia vs Meta", f"${diferencia:.2f}", delta="❌ Bajo la meta", delta_color="inverse")
            
            st.progress(min(weekly['porcentaje_meta'] / 100, 1.0))
            st.caption(f"Progreso hacia la meta semanal: {weekly['porcentaje_meta']:.1f}%")
            
            # Registros de la semana
            st.markdown("---")
            st.subheader("📅 Registros de la Semana")
            
            week_records = []
            try:
                all_records = db.get_all_records(limit=100)
                for record in all_records:
                    try:
                        r_date = datetime.strptime(record.get('date', ''), '%Y-%m-%d').date()
                        if weekly['week_start'] <= r_date <= weekly['week_end']:
                            week_records.append(record)
                    except:
                        continue
            except:
                pass
            
            if week_records:
                for record in week_records:
                    with st.expander(f"📅 {record.get('date', 'Sin fecha')} - Ganancia Neta: ${float(record.get('net_profit', 0)):.2f}"):
                        col_h1, col_h2, col_h3 = st.columns(3)
                        col_h1.metric("Ingreso Bruto", f"${float(record.get('total_gross', 0)):.2f}")
                        col_h2.metric("Gastos", f"${float(record.get('total_expenses', 0)):.2f}")
                        col_h3.metric("Ganancia Neta", f"${float(record.get('net_profit', 0)):.2f}")
            else:
                st.info("No hay registros para esta semana aún.")
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Quota exceeded" in error_str:
                st.error("⚠️ **Límite de solicitudes excedido**")
                st.warning("Has excedido el límite de solicitudes a Google Sheets API. Por favor espera 1-2 minutos antes de intentar de nuevo.")
                st.info("💡 **Sugerencia:** La aplicación usa caché para reducir las llamadas. Evita hacer clic múltiples veces rápidamente.")
                if st.button("🔄 Limpiar caché y reintentar", key="clear_cache_main_weekly"):
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.error(f"Error cargando datos semanales: {e}")
    
    elif view_option == "📅 Mensual":
        # Obtener el mes seleccionado del sidebar
        today = datetime.now().date()
        current_year = today.year
        current_month = today.month
        
        # Obtener valores seleccionados (si existen en session_state, sino usar actuales)
        selected_year = st.session_state.get('year_selector', current_year)
        selected_month = st.session_state.get('month_selector', current_month - 1) + 1
        
        months_list = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        st.subheader(f"📅 Resumen Mensual")
        st.caption(f"{months_list[selected_month - 1]} {selected_year}")
        
        try:
            monthly = db.get_monthly_summary(meta_neta_objetivo, selected_year, selected_month)
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Días registrados", f"{monthly['days']}/{monthly['days_in_month']}")
            col2.metric("💰 Ingresos Totales", f"${monthly['total_income']:.2f}")
            col3.metric("💸 Gastos Totales", f"${monthly['total_expenses']:.2f}")
            col4.metric("🏆 Ganancia Neta", f"${monthly['total_profit']:.2f}")
            
            st.markdown("---")
            
            # Meta mensual
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.metric(f"Meta Mensual ({monthly['days_in_month']} días)", f"${monthly['meta_mensual']:.2f}")
            with col_meta2:
                diferencia = monthly['diferencia_meta']
                if diferencia >= 0:
                    st.metric("Diferencia vs Meta", f"+${diferencia:.2f}", delta="✅ Sobre la meta")
                else:
                    st.metric("Diferencia vs Meta", f"${diferencia:.2f}", delta="❌ Bajo la meta", delta_color="inverse")
            
            st.progress(min(monthly['porcentaje_meta'] / 100, 1.0))
            st.caption(f"Progreso hacia la meta mensual: {monthly['porcentaje_meta']:.1f}%")
            
            # Registros del mes
            st.markdown("---")
            st.subheader("📅 Registros del Mes")
            
            month_records = []
            try:
                all_records = db.get_all_records(limit=100)
                for record in all_records:
                    try:
                        r_date = datetime.strptime(record.get('date', ''), '%Y-%m-%d').date()
                        if monthly['month_start'] <= r_date <= monthly['month_end']:
                            month_records.append(record)
                    except:
                        continue
            except:
                pass
            
            if month_records:
                for record in month_records:
                    with st.expander(f"📅 {record.get('date', 'Sin fecha')} - Ganancia Neta: ${float(record.get('net_profit', 0)):.2f}"):
                        col_h1, col_h2, col_h3 = st.columns(3)
                        col_h1.metric("Ingreso Bruto", f"${float(record.get('total_gross', 0)):.2f}")
                        col_h2.metric("Gastos", f"${float(record.get('total_expenses', 0)):.2f}")
                        col_h3.metric("Ganancia Neta", f"${float(record.get('net_profit', 0)):.2f}")
                        
                        col_h4, col_h5 = st.columns(2)
                        col_h4.write(f"**Millas:** {float(record.get('miles_driven', 0)):.1f} mi")
                        col_h5.write(f"**Combustible:** ${float(record.get('fuel_cost', 0)):.2f}")
            else:
                st.info("No hay registros para este mes aún.")
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Quota exceeded" in error_str:
                st.error("⚠️ **Límite de solicitudes excedido**")
                st.warning("Has excedido el límite de solicitudes a Google Sheets API. Por favor espera 1-2 minutos antes de intentar de nuevo.")
                st.info("💡 **Sugerencia:** La aplicación usa caché para reducir las llamadas. Evita hacer clic múltiples veces rápidamente.")
                if st.button("🔄 Limpiar caché y reintentar", key="clear_cache_main_monthly"):
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.error(f"Error cargando datos mensuales: {e}")
