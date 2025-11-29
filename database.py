import sqlite3
import datetime
from typing import Optional, List, Dict
import os

DB_PATH = "driver_finances.db"

def init_database():
    """Inicializa la base de datos y crea las tablas si no existen"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla principal para registros diarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            mpg REAL,
            gas_price REAL,
            meta_neta_objetivo REAL,
            uber_earnings REAL,
            lyft_earnings REAL,
            cash_tips REAL,
            odo_start INTEGER,
            odo_end INTEGER,
            miles_driven REAL,
            gallons_used REAL,
            fuel_cost REAL,
            food_cost REAL,
            misc_cost REAL,
            additional_expenses TEXT,
            additional_income TEXT,
            wear_and_tear REAL,
            total_gross REAL,
            total_expenses REAL,
            net_profit REAL,
            expense_ratio REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Agregar columnas adicionales si no existen (para bases de datos existentes)
    try:
        cursor.execute('ALTER TABLE daily_records ADD COLUMN additional_expenses TEXT')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    try:
        cursor.execute('ALTER TABLE daily_records ADD COLUMN additional_income TEXT')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    # Tabla para configuración del vehículo (valores por defecto)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_config (
            id INTEGER PRIMARY KEY,
            mpg REAL DEFAULT 35.0,
            gas_price REAL DEFAULT 3.10,
            meta_neta_objetivo REAL DEFAULT 200.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insertar configuración por defecto si no existe
    cursor.execute('SELECT COUNT(*) FROM vehicle_config')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO vehicle_config (id, mpg, gas_price, meta_neta_objetivo)
            VALUES (1, 35.0, 3.10, 200.0)
        ''')
    
    conn.commit()
    conn.close()

def get_vehicle_config() -> Dict:
    """Obtiene la configuración del vehículo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT mpg, gas_price, meta_neta_objetivo FROM vehicle_config WHERE id = 1')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'mpg': result[0],
            'gas_price': result[1],
            'meta_neta_objetivo': result[2]
        }
    return {'mpg': 35.0, 'gas_price': 3.10, 'meta_neta_objetivo': 200.0}

def update_vehicle_config(mpg: float, gas_price: float, meta_neta_objetivo: float):
    """Actualiza la configuración del vehículo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vehicle_config 
        SET mpg = ?, gas_price = ?, meta_neta_objetivo = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (mpg, gas_price, meta_neta_objetivo))
    conn.commit()
    conn.close()

def save_daily_record(data: Dict, record_date: Optional[str] = None) -> bool:
    """Guarda un registro diario en la base de datos
    
    Args:
        data: Diccionario con los datos del registro
        record_date: Fecha del registro en formato ISO (YYYY-MM-DD). Si es None, usa la fecha de hoy.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Usar la fecha proporcionada o la fecha de hoy
        if record_date:
            target_date = record_date
        else:
            target_date = datetime.date.today().isoformat()
        
        # Verificar si ya existe un registro para esta fecha
        cursor.execute('SELECT id FROM daily_records WHERE date = ?', (target_date,))
        existing = cursor.fetchone()
        
        # Convertir gastos e ingresos adicionales a JSON si son listas
        import json
        additional_expenses_json = None
        if 'additional_expenses' in data and data.get('additional_expenses'):
            if isinstance(data['additional_expenses'], list):
                additional_expenses_json = json.dumps(data['additional_expenses'])
            else:
                additional_expenses_json = data.get('additional_expenses')
        
        additional_income_json = None
        if 'additional_income' in data and data.get('additional_income'):
            if isinstance(data['additional_income'], list):
                additional_income_json = json.dumps(data['additional_income'])
            else:
                additional_income_json = data.get('additional_income')
        
        if existing:
            # Actualizar registro existente
            cursor.execute('''
                UPDATE daily_records SET
                    mpg = ?, gas_price = ?, meta_neta_objetivo = ?,
                    uber_earnings = ?, lyft_earnings = ?, cash_tips = ?,
                    odo_start = ?, odo_end = ?, miles_driven = ?,
                    gallons_used = ?, fuel_cost = ?, food_cost = ?,
                    misc_cost = ?, additional_expenses = ?, additional_income = ?, wear_and_tear = ?, total_gross = ?,
                    total_expenses = ?, net_profit = ?, expense_ratio = ?
                WHERE date = ?
            ''', (
                data.get('mpg'), data.get('gas_price'), data.get('meta_neta_objetivo'),
                data.get('uber_earnings'), data.get('lyft_earnings'), data.get('cash_tips'),
                data.get('odo_start'), data.get('odo_end'), data.get('miles_driven'),
                data.get('gallons_used'), data.get('fuel_cost'), data.get('food_cost'),
                data.get('misc_cost'), additional_expenses_json, additional_income_json, data.get('wear_and_tear'), data.get('total_gross'),
                data.get('total_expenses'), data.get('net_profit'), data.get('expense_ratio'),
                target_date
            ))
        else:
            # Insertar nuevo registro
            cursor.execute('''
                INSERT INTO daily_records (
                    date, mpg, gas_price, meta_neta_objetivo,
                    uber_earnings, lyft_earnings, cash_tips,
                    odo_start, odo_end, miles_driven,
                    gallons_used, fuel_cost, food_cost,
                    misc_cost, additional_expenses, additional_income, wear_and_tear, total_gross,
                    total_expenses, net_profit, expense_ratio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                target_date,
                data.get('mpg'), data.get('gas_price'), data.get('meta_neta_objetivo'),
                data.get('uber_earnings'), data.get('lyft_earnings'), data.get('cash_tips'),
                data.get('odo_start'), data.get('odo_end'), data.get('miles_driven'),
                data.get('gallons_used'), data.get('fuel_cost'), data.get('food_cost'),
                data.get('misc_cost'), additional_expenses_json, additional_income_json, data.get('wear_and_tear'), data.get('total_gross'),
                data.get('total_expenses'), data.get('net_profit'), data.get('expense_ratio')
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error guardando registro: {e}")
        return False

def get_today_record() -> Optional[Dict]:
    """Obtiene el registro de hoy si existe"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()
    cursor.execute('SELECT * FROM daily_records WHERE date = ?', (today,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))
    return None

def get_record_by_date(date: str) -> Optional[Dict]:
    """Obtiene un registro por fecha específica"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM daily_records WHERE date = ?', (date,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))
    return None

def get_last_record() -> Optional[Dict]:
    """Obtiene el último registro (más reciente por fecha)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM daily_records ORDER BY date DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))
    return None

def get_all_records(limit: int = 30) -> List[Dict]:
    """Obtiene todos los registros, ordenados por fecha descendente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM daily_records 
        ORDER BY date DESC 
        LIMIT ?
    ''', (limit,))
    
    columns = [description[0] for description in cursor.description]
    records = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return records

def get_statistics() -> Dict:
    """Obtiene estadísticas agregadas de todos los registros"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_days,
            SUM(total_gross) as total_income,
            SUM(total_expenses) as total_expenses,
            SUM(net_profit) as total_profit,
            AVG(net_profit) as avg_daily_profit,
            SUM(miles_driven) as total_miles,
            SUM(fuel_cost) as total_fuel_cost
        FROM daily_records
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return {
            'total_days': result[0] or 0,
            'total_income': result[1] or 0.0,
            'total_expenses': result[2] or 0.0,
            'total_profit': result[3] or 0.0,
            'avg_daily_profit': result[4] or 0.0,
            'total_miles': result[5] or 0.0,
            'total_fuel_cost': result[6] or 0.0
        }
    return {
        'total_days': 0,
        'total_income': 0.0,
        'total_expenses': 0.0,
        'total_profit': 0.0,
        'avg_daily_profit': 0.0,
        'total_miles': 0.0,
        'total_fuel_cost': 0.0
    }

def delete_record(date: str) -> bool:
    """Elimina un registro por fecha"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM daily_records WHERE date = ?', (date,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error eliminando registro: {e}")
        return False

def get_weekly_summary(meta_diaria: float) -> Dict:
    """Obtiene el resumen semanal (últimos 7 días)"""
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=6)  # Últimos 7 días incluyendo hoy
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as days,
            COALESCE(SUM(total_gross), 0) as total_income,
            COALESCE(SUM(total_expenses), 0) as total_expenses,
            COALESCE(SUM(net_profit), 0) as total_profit,
            COALESCE(SUM(miles_driven), 0) as total_miles
        FROM daily_records
        WHERE date >= ? AND date <= ?
    ''', (week_start.isoformat(), today.isoformat()))
    
    result = cursor.fetchone()
    conn.close()
    
    meta_semanal = meta_diaria * 7
    
    if result and result[0]:
        return {
            'days': result[0] or 0,
            'total_income': result[1] or 0.0,
            'total_expenses': result[2] or 0.0,
            'total_profit': result[3] or 0.0,
            'total_miles': result[4] or 0.0,
            'meta_semanal': meta_semanal,
            'diferencia_meta': (result[3] or 0.0) - meta_semanal,
            'porcentaje_meta': ((result[3] or 0.0) / meta_semanal * 100) if meta_semanal > 0 else 0
        }
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
    """Obtiene el resumen mensual (últimos 30 días)"""
    today = datetime.date.today()
    month_start = today - datetime.timedelta(days=29)  # Últimos 30 días incluyendo hoy
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as days,
            COALESCE(SUM(total_gross), 0) as total_income,
            COALESCE(SUM(total_expenses), 0) as total_expenses,
            COALESCE(SUM(net_profit), 0) as total_profit,
            COALESCE(SUM(miles_driven), 0) as total_miles
        FROM daily_records
        WHERE date >= ? AND date <= ?
    ''', (month_start.isoformat(), today.isoformat()))
    
    result = cursor.fetchone()
    conn.close()
    
    meta_mensual = meta_diaria * 30
    
    if result and result[0]:
        return {
            'days': result[0] or 0,
            'total_income': result[1] or 0.0,
            'total_expenses': result[2] or 0.0,
            'total_profit': result[3] or 0.0,
            'total_miles': result[4] or 0.0,
            'meta_mensual': meta_mensual,
            'diferencia_meta': (result[3] or 0.0) - meta_mensual,
            'porcentaje_meta': ((result[3] or 0.0) / meta_mensual * 100) if meta_mensual > 0 else 0
        }
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

# Inicializar la base de datos al importar el módulo
init_database()

