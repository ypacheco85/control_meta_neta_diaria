import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json

# Nombre de la hoja de cálculo y pestañas
SHEET_NAME = "App_Uber_2025"
WORKSHEET_DB = "Driver_Finances_DB"
WORKSHEET_CONFIG = "Config"

# --- CONEXIÓN CON GOOGLE SHEETS (CON CACHÉ) ---
@st.cache_resource(ttl=300)  # Cache por 5 minutos
def get_connection():
    """Conecta con Google Sheets usando los secretos de Streamlit (con caché)"""
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Cargar credenciales desde st.secrets
        credentials_dict = dict(st.secrets["gcp_service_account"])
        # Arreglar el formato de la llave privada
        if "private_key" in credentials_dict:
            credentials_dict["private_key"] = credentials_dict["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Abrir la hoja de cálculo por nombre
        try:
            sheet = client.open(SHEET_NAME)
            # Verificar que realmente obtuvimos un objeto Spreadsheet
            if sheet is None:
                raise Exception("No se pudo obtener el objeto Spreadsheet")
            return sheet
        except gspread.exceptions.SpreadsheetNotFound:
            st.error(f"❌ No se encontró el Google Sheet '{SHEET_NAME}'. Por favor:")
            st.info("1. Crea un Google Sheet con ese nombre exacto\n2. Compártelo con el email de la cuenta de servicio\n3. Verifica que tenga permisos de 'Editor'")
            return None
        except gspread.exceptions.APIError as api_error:
            error_str = str(api_error)
            # Manejar error 429 (Quota exceeded)
            if "429" in error_str or "Quota exceeded" in error_str:
                st.error("⚠️ **Límite de solicitudes excedido**")
                st.warning("Has excedido el límite de solicitudes a Google Sheets API. Por favor espera unos minutos antes de intentar de nuevo.")
                st.info("**Solución:**\n1. Espera 1-2 minutos antes de recargar\n2. La aplicación usa caché para reducir las llamadas\n3. Evita hacer clic múltiples veces rápidamente")
                return None
            elif "Response" in error_str or "200" in error_str:
                st.error(f"❌ Error de acceso al Google Sheet '{SHEET_NAME}'")
                st.warning("El Sheet existe pero puede haber un problema de permisos o acceso.")
                st.info("**Solución:**\n1. Verifica que el Google Sheet 'App_Uber_2025' existe\n2. Compártelo con el email de la cuenta de servicio (Editor)\n3. El email de la cuenta está en tus secrets de Streamlit (campo 'client_email')")
            else:
                st.error(f"Error de API: {error_str}")
            return None
        except Exception as sheet_error:
            error_str = str(sheet_error)
            # Manejar el caso específico de Response [200]
            if "Response" in error_str or "<Response" in error_str:
                st.error(f"❌ Error de conexión con Google Sheets")
                st.warning("Parece que hay un problema al acceder al Sheet, aunque la conexión fue exitosa.")
                st.info("**Posibles causas:**\n1. El Google Sheet no existe o tiene otro nombre\n2. La cuenta de servicio no tiene permisos\n3. El Sheet no está compartido correctamente")
                st.info("**Solución:**\n1. Verifica que existe un Google Sheet llamado exactamente 'App_Uber_2025'\n2. Compártelo con el email de la cuenta de servicio\n3. Dale permisos de 'Editor'")
            else:
                st.error(f"Error al abrir la hoja '{SHEET_NAME}': {error_str}")
                st.info("Verifica que el Google Sheet existe y está compartido con la cuenta de servicio")
            return None
    except KeyError as e:
        st.error(f"❌ Error de configuración: No se encontró 'gcp_service_account' en los secrets de Streamlit")
        st.info("Por favor configura los secrets de Streamlit. Ver STREAMLIT_SECRETS.md para más información.")
        return None
    except Exception as e:
        error_msg = str(e)
        # Si el error contiene información de respuesta HTTP, extraer solo el mensaje útil
        if "<Response" in error_msg:
            st.error(f"❌ Error de conexión con Google Sheets")
            st.info(f"Detalles: {error_msg}")
            st.info("Verifica:\n1. Que los secrets de Streamlit estén configurados correctamente\n2. Que el Google Sheet 'App_Uber_2025' exista\n3. Que la cuenta de servicio tenga permisos de acceso")
        else:
            st.error(f"Error al conectar con Google Sheets '{SHEET_NAME}': {error_msg}")
        return None

def init_worksheets():
    """Inicializa las hojas si no existen y crea los encabezados"""
    try:
        sheet = get_connection()
        if sheet is None:
            return
        
        # Inicializar hoja de configuración
        try:
            ws_config = sheet.worksheet(WORKSHEET_CONFIG)
            # Verificar si tiene datos
            if not ws_config.row_values(1):
                ws_config.update('A1:C1', [['MPG', 'Gas Price', 'Meta Neta Objetivo']])
            if not ws_config.row_values(2):
                ws_config.update('A2:C2', [[35.0, 3.10, 200.0]])
        except gspread.exceptions.WorksheetNotFound:
            ws_config = sheet.add_worksheet(title=WORKSHEET_CONFIG, rows=10, cols=10)
            # Crear encabezados
            ws_config.update('A1:C1', [['MPG', 'Gas Price', 'Meta Neta Objetivo']])
            # Valores por defecto
            ws_config.update('A2:C2', [[35.0, 3.10, 200.0]])
        
        # Inicializar hoja de registros
        try:
            ws_db = sheet.worksheet(WORKSHEET_DB)
            # Verificar si tiene encabezados
            headers = ws_db.row_values(1)
            if not headers or len(headers) < 17:
                # Crear encabezados si no existen
                headers = [
                    'Fecha', 'Uber Earnings', 'Lyft Earnings', 'Cash Tips', 'Additional Income',
                    'Odo Start', 'Odo End', 'Miles Driven', 'Gallons Used', 'Fuel Cost',
                    'Food Cost', 'Misc Cost', 'Additional Expenses', 'Wear And Tear',
                    'Total Gross', 'Total Expenses', 'Net Profit', 'Meta Neta Objetivo', 'Expense Ratio'
                ]
                ws_db.update('A1:S1', [headers])
        except gspread.exceptions.WorksheetNotFound:
            ws_db = sheet.add_worksheet(title=WORKSHEET_DB, rows=1000, cols=20)
            # Crear encabezados
            headers = [
                'Fecha', 'Uber Earnings', 'Lyft Earnings', 'Cash Tips', 'Additional Income',
                'Odo Start', 'Odo End', 'Miles Driven', 'Gallons Used', 'Fuel Cost',
                'Food Cost', 'Misc Cost', 'Additional Expenses', 'Wear And Tear',
                'Total Gross', 'Total Expenses', 'Net Profit', 'Meta Neta Objetivo', 'Expense Ratio'
            ]
            ws_db.update('A1:S1', [headers])
    except Exception as e:
        pass  # Se manejará cuando se use

# --- CONFIGURACIÓN DEL VEHÍCULO (Pestaña 'Config') ---
def get_vehicle_config() -> Dict:
    """Obtiene la configuración del vehículo desde Google Sheets"""
    try:
        sheet = get_connection()
        if sheet is None:
            return {'mpg': 35.0, 'gas_price': 3.10, 'meta_neta_objetivo': 200.0}
        ws = sheet.worksheet(WORKSHEET_CONFIG)
        
        # Leer valores de la fila 2 (A2, B2, C2)
        vals = ws.row_values(2)
        
        # Si la hoja está vacía, devolver valores por defecto
        if not vals or len(vals) < 3:
            return {'mpg': 35.0, 'gas_price': 3.10, 'meta_neta_objetivo': 200.0}
            
        return {
            'mpg': float(vals[0]) if vals[0] else 35.0,
            'gas_price': float(vals[1]) if len(vals) > 1 and vals[1] else 3.10,
            'meta_neta_objetivo': float(vals[2]) if len(vals) > 2 and vals[2] else 200.0
        }
    except Exception as e:
        return {'mpg': 35.0, 'gas_price': 3.10, 'meta_neta_objetivo': 200.0}

def update_vehicle_config(mpg: float, gas_price: float, meta_neta_objetivo: float):
    """Actualiza la configuración del vehículo en Google Sheets"""
    try:
        sheet = get_connection()
        if sheet is None:
            return
        ws = sheet.worksheet(WORKSHEET_CONFIG)
        # Actualizar celdas específicas
        ws.update('A2:C2', [[mpg, gas_price, meta_neta_objetivo]])
    except Exception as e:
        st.error(f"Error actualizando configuración: {e}")

# --- GESTIÓN DE REGISTROS (Pestaña 'Driver_Finances_DB') ---
def save_daily_record(data: Dict, record_date: Optional[str] = None) -> bool:
    """Guarda un registro diario en Google Sheets"""
    try:
        if record_date is None:
            record_date = datetime.now().date().isoformat()
        
        sheet = get_connection()
        if sheet is None:
            return False
        
        # Inicializar hojas si es necesario
        init_worksheets()
        
        ws = sheet.worksheet(WORKSHEET_DB)
        
        # Convertir listas a JSON
        additional_income_json = json.dumps(data.get('additional_income', []))
        additional_expenses_json = json.dumps(data.get('additional_expenses', []))
        
        # Preparar la fila de datos (orden estricto de columnas)
        row_data = [
            record_date,                                    # A: Fecha
            float(data.get('uber_earnings', 0)),          # B: Uber
            float(data.get('lyft_earnings', 0)),          # C: Lyft
            float(data.get('cash_tips', 0)),               # D: Propinas
            additional_income_json,                         # E: Ingresos Extra (JSON)
            int(data.get('odo_start', 0)),                 # F: Odo Inicio
            int(data.get('odo_end', 0)),                   # G: Odo Fin
            float(data.get('miles_driven', 0)),            # H: Millas
            float(data.get('gallons_used', 0)),            # I: Galones
            float(data.get('fuel_cost', 0)),               # J: Costo Gasolina
            float(data.get('food_cost', 0)),               # K: Comida
            float(data.get('misc_cost', 0)),               # L: Varios
            additional_expenses_json,                       # M: Gastos Extra (JSON)
            float(data.get('wear_and_tear', 0)),           # N: Desgaste
            float(data.get('total_gross', 0)),             # O: Bruto Total
            float(data.get('total_expenses', 0)),          # P: Gastos Total
            float(data.get('net_profit', 0)),              # Q: Neto Final
            float(data.get('meta_neta_objetivo', 0)),     # R: Meta del día
            float(data.get('expense_ratio', 0))           # S: Ratio
        ]
        
        # Buscar si ya existe la fecha (Columna A)
        try:
            cell = ws.find(record_date, in_column=1)
            # Si existe, actualizamos esa fila
            for i, val in enumerate(row_data):
                ws.update_cell(cell.row, i + 1, val)
        except gspread.exceptions.CellNotFound:
            # Si no existe, agregamos nueva fila
            ws.append_row(row_data)
            
        return True
    except Exception as e:
        st.error(f"Error guardando registro: {e}")
        return False

def get_record_by_date(date: str) -> Optional[Dict]:
    """Obtiene un registro por fecha específica"""
    try:
        sheet = get_connection()
        if sheet is None:
            return None
        
        # Inicializar hojas si es necesario
        init_worksheets()
        
        ws = sheet.worksheet(WORKSHEET_DB)
        
        cell = ws.find(date, in_column=1)
        row_values = ws.row_values(cell.row)
        
        # Mapear la lista de valores a un diccionario
        # gspread devuelve todo como strings, hay que convertir
        additional_income = []
        additional_expenses = []
        
        try:
            if len(row_values) > 4 and row_values[4]:
                additional_income = json.loads(row_values[4])
        except:
            pass
            
        try:
            if len(row_values) > 12 and row_values[12]:
                additional_expenses = json.loads(row_values[12])
        except:
            pass
        
        def safe_float(val, default=0.0):
            try:
                return float(val) if val else default
            except:
                return default
        
        def safe_int(val, default=0):
            try:
                return int(float(val)) if val else default
            except:
                return default
        
        return {
            'date': row_values[0] if len(row_values) > 0 else '',
            'uber_earnings': safe_float(row_values[1] if len(row_values) > 1 else 0),
            'lyft_earnings': safe_float(row_values[2] if len(row_values) > 2 else 0),
            'cash_tips': safe_float(row_values[3] if len(row_values) > 3 else 0),
            'additional_income': additional_income,
            'odo_start': safe_int(row_values[5] if len(row_values) > 5 else 0),
            'odo_end': safe_int(row_values[6] if len(row_values) > 6 else 0),
            'miles_driven': safe_float(row_values[7] if len(row_values) > 7 else 0),
            'gallons_used': safe_float(row_values[8] if len(row_values) > 8 else 0),
            'fuel_cost': safe_float(row_values[9] if len(row_values) > 9 else 0),
            'food_cost': safe_float(row_values[10] if len(row_values) > 10 else 0),
            'misc_cost': safe_float(row_values[11] if len(row_values) > 11 else 0),
            'additional_expenses': additional_expenses,
            'wear_and_tear': safe_float(row_values[13] if len(row_values) > 13 else 0),
            'total_gross': safe_float(row_values[14] if len(row_values) > 14 else 0),
            'total_expenses': safe_float(row_values[15] if len(row_values) > 15 else 0),
            'net_profit': safe_float(row_values[16] if len(row_values) > 16 else 0),
            'meta_neta_objetivo': safe_float(row_values[17] if len(row_values) > 17 else 0),
            'expense_ratio': safe_float(row_values[18] if len(row_values) > 18 else 0)
        }
    except gspread.exceptions.CellNotFound:
        return None
    except Exception as e:
        return None

def get_last_record() -> Optional[Dict]:
    """Obtiene el último registro ingresado para sacar el odómetro final"""
    try:
        sheet = get_connection()
        if sheet is None:
            return None
        ws = sheet.worksheet(WORKSHEET_DB)
        all_rows = ws.get_all_values()
        
        if len(all_rows) < 2:  # Solo encabezados o vacía
            return None
        
        # Buscar el último registro con datos (saltando encabezado)
        for i in range(len(all_rows) - 1, 0, -1):
            row = all_rows[i]
            if len(row) > 6 and row[0] and row[6]:  # Tiene fecha y odómetro final
                try:
                    return {
                        'odo_end': int(float(row[6])),
                        'date': row[0]
                    }
                except:
                    continue
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=60)  # Cache por 1 minuto para reducir llamadas a la API
def get_all_records(limit: int = 30) -> List[Dict]:
    """Obtiene todos los registros, ordenados por fecha descendente (con caché)"""
    try:
        sheet = get_connection()
        if sheet is None:
            return []
        
        # Inicializar hojas si es necesario
        init_worksheets()
        
        ws = sheet.worksheet(WORKSHEET_DB)
        
        # Obtener todos los registros, saltando el encabezado
        all_rows = ws.get_all_values()
        
        if len(all_rows) < 2:
            return []
        
        records = []
        headers = all_rows[0]
        
        # Mapeo de nombres de columnas
        column_map = {
            'Fecha': 'date',
            'Uber Earnings': 'uber_earnings',
            'Lyft Earnings': 'lyft_earnings',
            'Cash Tips': 'cash_tips',
            'Additional Income': 'additional_income',
            'Odo Start': 'odo_start',
            'Odo End': 'odo_end',
            'Miles Driven': 'miles_driven',
            'Gallons Used': 'gallons_used',
            'Fuel Cost': 'fuel_cost',
            'Food Cost': 'food_cost',
            'Misc Cost': 'misc_cost',
            'Additional Expenses': 'additional_expenses',
            'Wear And Tear': 'wear_and_tear',
            'Total Gross': 'total_gross',
            'Total Expenses': 'total_expenses',
            'Net Profit': 'net_profit',
            'Meta Neta Objetivo': 'meta_neta_objetivo',
            'Expense Ratio': 'expense_ratio'
        }
        
        # Procesar filas (saltando encabezado)
        for row in all_rows[1:]:
            if not row[0]:  # Si no hay fecha, saltar
                continue
                
            try:
                record = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        value = row[i]
                        field_name = column_map.get(header, header.lower().replace(' ', '_'))
                        
                        # Convertir valores según el tipo
                        if header == 'Fecha':
                            record['date'] = value
                        elif header == 'Additional Income':
                            try:
                                record['additional_income'] = json.loads(value) if value else []
                            except:
                                record['additional_income'] = []
                        elif header == 'Additional Expenses':
                            try:
                                record['additional_expenses'] = json.loads(value) if value else []
                            except:
                                record['additional_expenses'] = []
                        elif header in ['Odo Start', 'Odo End']:
                            record[field_name] = int(float(value)) if value else 0
                        elif header in ['Uber Earnings', 'Lyft Earnings', 'Cash Tips', 'Miles Driven', 
                                     'Gallons Used', 'Fuel Cost', 'Food Cost', 'Misc Cost', 
                                     'Wear And Tear', 'Total Gross', 'Total Expenses', 'Net Profit',
                                     'Meta Neta Objetivo', 'Expense Ratio']:
                            record[field_name] = float(value) if value else 0.0
                        else:
                            record[field_name] = value
                
                if record.get('date'):  # Solo agregar si tiene fecha
                    records.append(record)
            except Exception as e:
                continue
        
        # Ordenar por fecha descendente
        try:
            records.sort(key=lambda x: x.get('date', ''), reverse=True)
        except:
            pass
        
        return records[:limit]
    except Exception as e:
        return []

def get_statistics() -> Dict:
    """Obtiene estadísticas agregadas de todos los registros - usa datos cacheados"""
    try:
        # Usar get_all_records que ya tiene caché
        records = get_all_records(limit=365)
        
        if not records:
            return {
                'total_days': 0,
                'total_income': 0.0,
                'total_expenses': 0.0,
                'total_profit': 0.0,
                'avg_daily_profit': 0.0,
                'total_miles': 0.0,
                'total_fuel_cost': 0.0
            }
        
        total_income = sum(float(r.get('total_gross', 0)) for r in records)
        total_expenses = sum(float(r.get('total_expenses', 0)) for r in records)
        total_profit = sum(float(r.get('net_profit', 0)) for r in records)
        total_miles = sum(float(r.get('miles_driven', 0)) for r in records)
        total_fuel_cost = sum(float(r.get('fuel_cost', 0)) for r in records)
        
        count = len(records)
        
        return {
            'total_days': count,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'avg_daily_profit': total_profit / count if count > 0 else 0.0,
            'total_miles': total_miles,
            'total_fuel_cost': total_fuel_cost
        }
    except Exception as e:
        return {
            'total_days': 0,
            'total_income': 0.0,
            'total_expenses': 0.0,
            'total_profit': 0.0,
            'avg_daily_profit': 0.0,
            'total_miles': 0.0,
            'total_fuel_cost': 0.0
        }

def get_weekly_summary(meta_diaria: float) -> Dict:
    """Obtiene el resumen semanal (últimos 7 días) - usa datos cacheados"""
    try:
        # Usar get_all_records que ya tiene caché
        records = get_all_records(limit=100)
        today = datetime.now().date()
        week_start = today - timedelta(days=6)
        
        total_income = 0.0
        total_expenses = 0.0
        total_profit = 0.0
        total_miles = 0.0
        days_count = 0
        
        for r in records:
            try:
                r_date = datetime.strptime(r.get('date', ''), '%Y-%m-%d').date()
                if week_start <= r_date <= today:
                    total_income += float(r.get('total_gross', 0))
                    total_expenses += float(r.get('total_expenses', 0))
                    total_profit += float(r.get('net_profit', 0))
                    total_miles += float(r.get('miles_driven', 0))
                    days_count += 1
            except:
                continue
        
        meta_semanal = meta_diaria * 7
        
        return {
            'days': days_count,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'total_miles': total_miles,
            'meta_semanal': meta_semanal,
            'diferencia_meta': total_profit - meta_semanal,
            'porcentaje_meta': (total_profit / meta_semanal * 100) if meta_semanal > 0 else 0.0
        }
    except Exception as e:
        meta_semanal = meta_diaria * 7
        return {
            'days': 0,
            'total_income': 0.0,
            'total_expenses': 0.0,
            'total_profit': 0.0,
            'total_miles': 0.0,
            'meta_semanal': meta_semanal,
            'diferencia_meta': -meta_semanal,
            'porcentaje_meta': 0.0
        }

def get_monthly_summary(meta_diaria: float) -> Dict:
    """Obtiene el resumen mensual (últimos 30 días) - usa datos cacheados"""
    try:
        # Usar get_all_records que ya tiene caché
        records = get_all_records(limit=100)
        today = datetime.now().date()
        month_start = today - timedelta(days=29)
        
        total_income = 0.0
        total_expenses = 0.0
        total_profit = 0.0
        total_miles = 0.0
        days_count = 0
        
        for r in records:
            try:
                r_date = datetime.strptime(r.get('date', ''), '%Y-%m-%d').date()
                if month_start <= r_date <= today:
                    total_income += float(r.get('total_gross', 0))
                    total_expenses += float(r.get('total_expenses', 0))
                    total_profit += float(r.get('net_profit', 0))
                    total_miles += float(r.get('miles_driven', 0))
                    days_count += 1
            except:
                continue
        
        meta_mensual = meta_diaria * 30
        
        return {
            'days': days_count,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'total_miles': total_miles,
            'meta_mensual': meta_mensual,
            'diferencia_meta': total_profit - meta_mensual,
            'porcentaje_meta': (total_profit / meta_mensual * 100) if meta_mensual > 0 else 0.0
        }
    except Exception as e:
        meta_mensual = meta_diaria * 30
        return {
            'days': 0,
            'total_income': 0.0,
            'total_expenses': 0.0,
            'total_profit': 0.0,
            'total_miles': 0.0,
            'meta_mensual': meta_mensual,
            'diferencia_meta': -meta_mensual,
            'porcentaje_meta': 0.0
        }

def delete_record(date: str) -> bool:
    """Elimina un registro por fecha"""
    try:
        sheet = get_connection()
        if sheet is None:
            return False
        ws = sheet.worksheet(WORKSHEET_DB)
        cell = ws.find(date, in_column=1)
        ws.delete_rows(cell.row)
        return True
    except Exception as e:
        return False
