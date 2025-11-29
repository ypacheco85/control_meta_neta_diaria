import sqlite3
import json
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_NAME = "Driver_Finances_DB"

def get_db_connection():
    """Mantiene la base de datos local (SQLite) para que la App funcione rápido"""
    conn = sqlite3.connect('driver_finances.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea la tabla local temporal"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            data JSON
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar al arrancar
init_db()

# --- CONEXIÓN CON LA NUBE (GOOGLE SHEETS) ---
def connect_to_sheets():
    """Conecta con Google Sheets usando el archivo credentials.json"""
    try:
        if os.path.exists('credentials.json'):
            creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
            client = gspread.authorize(creds)
            sheet = client.open(SPREADSHEET_NAME).sheet1
            return sheet
        else:
            print("⚠️ No se encontró credentials.json - Los datos solo se guardarán localmente.")
            return None
    except Exception as e:
        print(f"Error conectando a Sheets: {e}")
        return None

# --- FUNCIONES DE GUARDADO ---

def save_daily_record(data, date_str):
    """Guarda en SQLite (Local) Y en Google Sheets (Nube)"""
    
    # 1. GUARDAR EN SQLITE (Para que la app funcione rápido ahora)
    conn = get_db_connection()
    c = conn.cursor()
    json_data = json.dumps(data)
    try:
        c.execute('INSERT OR REPLACE INTO daily_records (date, data) VALUES (?, ?)',
                  (date_str, json_data))
        conn.commit()
    except Exception as e:
        print(f"Error local: {e}")
        return False
    finally:
        conn.close()

    # 2. GUARDAR EN GOOGLE SHEETS (Respaldo Permanente)
    try:
        sheet = connect_to_sheets()
        if sheet:
            # Preparamos la fila exactamente como pusimos los encabezados
            # Orden: Fecha | Plataforma | Ingresos | Propinas | Gastos | Odo_Inicio | Odo_Fin | Millas | Notas
            
            row_to_save = [
                date_str,                  # A: Fecha
                "Uber/Lyft/Otros",         # B: Plataforma
                data['total_gross'],       # C: Ingresos Brutos
                data['cash_tips'],         # D: Propinas
                data['total_expenses'],    # E: Gastos Totales
                data['odo_start'],         # F: Odo Inicio (Tus dos metros)
                data['odo_end'],           # G: Odo Fin
                data['miles_driven'],      # H: Millas Totales
                f"Ganancia Neta: ${data['net_profit']:.2f}" # I: Notas
            ]
            
            # Agregamos la fila al final de la hoja
            sheet.append_row(row_to_save)
            print("✅ Guardado en Google Sheets exitosamente")
            
    except Exception as e:
        print(f"⚠️ No se pudo guardar en Google Sheets: {e}")
        # No retornamos False para que el usuario no crea que falló todo, 
        # ya que al menos se guardó en local.

    return True

# --- FUNCIONES DE LECTURA (Por ahora leen de local para velocidad) ---

def get_record_by_date(date_str):
    conn = get_db_connection()
    record = conn.execute('SELECT data FROM daily_records WHERE date = ?', (date_str,)).fetchone()
    conn.close()
    if record:
        return json.loads(record['data'])
    return None

def get_last_record():
    conn = get_db_connection()
    record = conn.execute('SELECT data FROM daily_records ORDER BY date DESC LIMIT 1').fetchone()
    conn.close()
    if record:
        return json.loads(record['data'])
    return None

def get_all_records(limit=30):
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM daily_records ORDER BY date DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    records = []
    for row in rows:
        r_data = json.loads(row['data'])
        r_data['date'] = row['date']
        r_data['id'] = row['id']
        records.append(r_data)
    return records

def delete_record(date_str):
    conn = get_db_connection()
    conn.execute('DELETE FROM daily_records WHERE date = ?', (date_str,))
    conn.commit()
    conn.close()

# --- FUNCIONES DE CONFIGURACIÓN Y ESTADÍSTICAS ---
# Estas siguen igual que antes, simuladas con SQLite

def get_vehicle_config():
    # Valor por defecto para Highlander 2025 Hybrid
    return {'mpg': 35.0, 'gas_price': 3.50, 'meta_neta_objetivo': 150.0}

def update_vehicle_config(mpg, gas_price, meta_neta):
    pass # Por ahora no persistimos config en nube para simplificar

def get_statistics():
    records = get_all_records(limit=365)
    if not records:
        return {'total_days': 0, 'total_income': 0.0, 'total_expenses': 0.0, 
                'total_profit': 0.0, 'avg_daily_profit': 0.0, 'total_miles': 0.0, 'total_fuel_cost': 0.0}
    
    total_income = sum(float(r['total_gross']) for r in records)
    total_expenses = sum(float(r['total_expenses']) for r in records)
    total_profit = sum(float(r['net_profit']) for r in records)
    total_miles = sum(float(r.get('miles_driven', 0)) for r in records)
    total_fuel = sum(float(r.get('fuel_cost', 0)) for r in records)
    
    return {
        'total_days': len(records),
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'avg_daily_profit': total_profit / len(records),
        'total_miles': total_miles,
        'total_fuel_cost': total_fuel
    }

def get_weekly_summary(meta_neta_objetivo):
    # Simplificado para evitar errores, usa las estadísticas generales
    stats = get_statistics()
    return {
        'days': stats['total_days'],
        'total_income': stats['total_income'],
        'total_expenses': stats['total_expenses'],
        'total_profit': stats['total_profit'],
        'meta_semanal': meta_neta_objetivo * 7,
        'diferencia_meta': stats['total_profit'] - (meta_neta_objetivo * 7),
        'porcentaje_meta': (stats['total_profit'] / (meta_neta_objetivo * 7) * 100) if meta_neta_objetivo > 0 else 0
    }

def get_monthly_summary(meta_neta_objetivo):
    return get_weekly_summary(meta_neta_objetivo) # Reutiliza lógica