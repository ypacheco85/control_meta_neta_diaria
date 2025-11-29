import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json

# --- CONEXIÓN CON GOOGLE SHEETS ---
def get_connection():
    """Conecta con Google Sheets usando los secretos de Streamlit"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Cargar credenciales desde st.secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Arreglar el formato de la llave privada si es necesario
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Abrir la hoja de cálculo por nombre
    try:
        sheet = client.open("App_Uber_2025")
        return sheet
    except Exception as e:
        st.error(f"Error al conectar con la hoja 'App_Uber_2025': {e}")
        st.stop()

# --- CONFIGURACIÓN DEL VEHÍCULO (Pestaña 'Config') ---
def get_vehicle_config():
    try:
        sh = get_connection()
        ws = sh.worksheet("Config")
        
        # Leer valores de la fila 2 (A2, B2, C2)
        # Asumimos orden: MPG, Gas Price, Meta
        vals = ws.row_values(2)
        
        # Si la hoja está vacía, devolver valores por defecto
        if not vals:
            return {'mpg': 25.0, 'gas_price': 3.50, 'meta_neta_objetivo': 150.0}
            
        return {
            'mpg': float(vals[0]) if len(vals) > 0 else 25.0,
            'gas_price': float(vals[1]) if len(vals) > 1 else 3.50,
            'meta_neta_objetivo': float(vals[2]) if len(vals) > 2 else 150.0
        }
    except Exception:
        return {'mpg': 25.0, 'gas_price': 3.50, 'meta_neta_objetivo': 150.0}

def update_vehicle_config(mpg, gas_price, meta_neta_objetivo):
    sh = get_connection()
    ws = sh.worksheet("Config")
    # Actualizar celdas específicas
    ws.update_acell('A2', mpg)
    ws.update_acell('B2', gas_price)
    ws.update_acell('C2', meta_neta_objetivo)

# --- GESTIÓN DE REGISTROS (Pestaña 'Driver_Finances_DB') ---
def save_daily_record(data, date_str):
    sh = get_connection()
    ws = sh.worksheet("Driver_Finances_DB")
    
    # Preparar la fila de datos (Orden estricto de columnas)
    # Convertimos listas (ingresos extra) a texto JSON para guardarlas en una celda
    row_data = [
        date_str,                                   # A: Fecha
        data.get('uber_earnings', 0),               # B: Uber
        data.get('lyft_earnings', 0),               # C: Lyft
        data.get('cash_tips', 0),                   # D: Propinas
        json.dumps(data.get('additional_income', [])), # E: Ingresos Extra (JSON)
        data.get('odo_start', 0),                   # F: Odo Inicio
        data.get('odo_end', 0),                     # G: Odo Fin
        data.get('miles_driven', 0),                # H: Millas
        data.get('fuel_cost', 0),                   # I: Costo Gasolina
        data.get('food_cost', 0),                   # J: Comida
        data.get('misc_cost', 0),                   # K: Varios
        json.dumps(data.get('additional_expenses', [])), # L: Gastos Extra (JSON)
        data.get('total_gross', 0),                 # M: Bruto Total
        data.get('total_expenses', 0),              # N: Gastos Total
        data.get('net_profit', 0),                  # O: Neto Final
        data.get('meta_neta_objetivo', 0),          # P: Meta del día
        data.get('expense_ratio', 0)                # Q: Ratio
    ]
    
    # Buscar si ya existe la fecha (Columna A)
    try:
        cell = ws.find(date_str, in_column=1)
        # Si existe, actualizamos esa fila
        for i, val in enumerate(row_data):
            ws.update_cell(cell.row, i + 1, val)
    except gspread.exceptions.CellNotFound:
        # Si no existe, agregamos nueva fila
        ws.append_row(row_data)
        
    return True

def get_record_by_date(date_str):
    sh = get_connection()
    ws = sh.worksheet("Driver_Finances_DB")
    
    try:
        cell = ws.find(date_str, in_column=1)
        row_values = ws.row_values(cell.row)
        
        # Mapear la lista de valores a un diccionario (debe coincidir con save_daily_record)
        # Nota: gspread devuelve todo como strings, hay que convertir a float/int
        return {
            'date': row_values[0],
            'uber_earnings': float(row_values[1]),
            'lyft_earnings': float(row_values[2]),
            'cash_tips': float(row_values[3]),
            'additional_income': row_values[4], # Se decodifica en la app principal
            'odo_start': float(row_values[5]),
            'odo_end': float(row_values[6]),
            'miles_driven': float(row_values[7]),
            'fuel_cost': float(row_values[8]),
            'food_cost': float(row_values[9]),
            'misc_cost': float(row_values[10]),
            'additional_expenses': row_values[11], # Se decodifica en la app principal
            'total_gross': float(row_values[12]),
            'total_expenses': float(row_values[13]),
            'net_profit': float(row_values[14]),
            'meta_neta_objetivo': float(row_values[15]) if len(row_values) > 15 else 0
        }
    except gspread.exceptions.CellNotFound:
        return None
    except Exception as e:
        print(f"Error leyendo registro: {e}")
        return None

def get_last_record():
    """Obtiene el último registro ingresado para sacar el odómetro final"""
    sh = get_connection()
    ws = sh.worksheet("Driver_Finances_DB")
    all_rows = ws.get_all_values()
    
    if len(all_rows) < 2: # Solo encabezados o vacía
        return None
        
    # Asumimos que el último registro está al final. 
    # Para ser más exactos podríamos ordenar por fecha, pero esto suele bastar.
    last_row = all_rows[-1]
    return {'odo_end': last_row[6]} # Indice 6 es Columna G (Odo Fin)

def delete_record(date_str):
    sh = get_connection()
    ws = sh.worksheet("Driver_Finances_DB")
    try:
        cell = ws.find(date_str, in_column=1)
        ws.delete_rows(cell.row)
    except:
        pass

# --- ESTADÍSTICAS (Calculadas en vivo desde Sheets) ---
def get_all_records(limit=30):
    sh = get_connection()
    ws = sh.worksheet("Driver_Finances_DB")
    # Obtener todos los registros, saltando el encabezado
    raw_data = ws.get_all_records()
    
    # Ordenar por fecha descendente (más reciente primero)
    # Asegúrate de que tus fechas en Excel sean YYYY-MM-DD
    try:
        sorted_data = sorted(raw_data, key=lambda x: x['Fecha'], reverse=True)
    except:
        sorted_data = raw_data
        
    return sorted_data[:limit]

def get_weekly_summary(meta_target):
    # Esta función requiere lógica de filtrado de fechas
    # Para simplificar, obtenemos todo y filtramos en Python
    records = get_all_records(limit=100)
    today = datetime.now().date()
    start_week = today - timedelta(days=6)
    
    total_income = 0
    total_expenses = 0
    total_profit = 0
    days_count = 0
    
    for r in records:
        try:
            r_date = datetime.strptime(r['Fecha'], '%Y-%m-%d').date()
            if start_week <= r_date <= today:
                total_income += float(r['Ingresos'] if 'Ingresos' in r else r.get('Bruto Total', 0))
                total_expenses += float(r['Gastos'] if 'Gastos' in r else r.get('Gastos Total', 0))
                total_profit += float(r['Ganancia'] if 'Ganancia' in r else r.get('Neto Final', 0))
                days_count += 1
        except:
            continue
            
    meta_semanal = meta_target * 7
    return {
        'days': days_count,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'meta_semanal': meta_semanal,
        'diferencia_meta': total_profit - meta_semanal,
        'porcentaje_meta': (total_profit / meta_semanal * 100) if meta_semanal > 0 else 0
    }

def get_monthly_summary(meta_target):
    records = get_all_records(limit=100)
    today = datetime.now().date()
    start_month = today - timedelta(days=30)
    
    total_income = 0
    total_expenses = 0
    total_profit = 0
    days_count = 0
    
    for r in records:
        try:
            r_date = datetime.strptime(r['Fecha'], '%Y-%m-%d').date()
            if start_month <= r_date <= today:
                 total_income += float(r['Ingresos'] if 'Ingresos' in r else r.get('Bruto Total', 0))
                 total_expenses += float(r['Gastos'] if 'Gastos' in r else r.get('Gastos Total', 0))
                 total_profit += float(r['Ganancia'] if 'Ganancia' in r else r.get('Neto Final', 0))
                 days_count += 1
        except:
            continue
            
    meta_mensual = meta_target * 30
    return {
        'days': days_count,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'meta_mensual': meta_mensual,
        'diferencia_meta': total_profit - meta_mensual,
        'porcentaje_meta': (total_profit / meta_mensual * 100) if meta_mensual > 0 else 0
    }

def get_statistics():
    records = get_all_records(limit=365)
    if not records:
        return {'total_days': 0, 'total_income': 0, 'total_expenses': 0, 'total_profit': 0, 
                'avg_daily_profit': 0, 'total_miles': 0, 'total_fuel_cost': 0}
    
    t_income = sum(float(r.get('Bruto Total', 0)) for r in records)
    t_exp = sum(float(r.get('Gastos Total', 0)) for r in records)
    t_profit = sum(float(r.get('Neto Final', 0)) for r in records)
    t_miles = sum(float(r.get('Millas', 0)) for r in records)
    t_fuel = sum(float(r.get('Costo Gasolina', 0)) for r in records)
    
    count = len(records)
    
    return {
        'total_days': count,
        'total_income': t_income,
        'total_expenses': t_exp,
        'total_profit': t_profit,
        'avg_daily_profit': t_profit / count if count > 0 else 0,
        'total_miles': t_miles,
        'total_fuel_cost': t_fuel
    }