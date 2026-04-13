import requests
import json
import pandas as pd
from datetime import datetime
import argparse
import time
import os

# OpenAQ API v3
API_KEY = "f7d1cdb86501e027edfe02aca5094351ce53f2cb1b13133ffbb8f14950fbc64c"
BASE_URL = "https://api.openaq.org/v3"

headers = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}

# Verified Station IDs for RMCAB (Provider 158) based on user's list
STATIONS = {
    8518: "Guaymaral", 8519: "Kennedy", 8520: "Puente Aranda",
    8522: "Suba", 8523: "Tunal", 8524: "Usaquen",
    10812: "Las Ferias", 10705: "San Cristobal", 10677: "Carvajal - Sevillana",
    10535: "Centro de Alto Rendimiento", 10499: "Fontibon", 10730: "MinAmbiente",
    10626: "Jazmin", 10490: "Ciudad Bolivar", 10848: "Bolivia",
    268068: "Colina", 10841: "Bosa", 8025: "Usme", 268067: "Movil Fontibon"
}

def fetch_hourly_measurements(location_id, location_name, start_date, end_date):
    sensor_url = f"{BASE_URL}/locations/{location_id}/sensors"
    try:
        s_res = requests.get(sensor_url, headers=headers, timeout=15)
    except Exception as e:
         print(f"    !!! Error fetching sensors for {location_name}: {e}")
         return []

    if s_res.status_code == 429:
        print(f"    !!! RATE LIMIT (429) hit when fetching sensors. Sleeping 60s...")
        time.sleep(60)
        s_res = requests.get(sensor_url, headers=headers, timeout=15)

    all_meas = []
    if s_res.status_code == 200:
        sensors = s_res.json().get('results', [])
        for sensor in sensors:
            s_id = sensor['id']
            p_name = sensor['parameter']['name']
            u_name = sensor['parameter']['units']
            
            print(f"    * {location_name}: Fetching sensor {s_id} ({p_name})...")
            
            page = 1
            while True:
                meas_url = f"{BASE_URL}/sensors/{s_id}/measurements"
                params = {
                    "datetime_from": start_date,
                    "datetime_to": end_date,
                    "limit": 1000,
                    "page": page
                }
                
                success = False
                results = []
                for attempt in range(5): # Up to 5 attempts to respect limits
                    try:
                        m_res = requests.get(meas_url, headers=headers, params=params, timeout=30)
                        if m_res.status_code == 200:
                            data = m_res.json()
                            results = data.get('results', [])
                            success = True
                            break
                        elif m_res.status_code == 429:
                            print(f"      - Rate limit (429) hit on page {page} (Attempt {attempt+1}/5). Sleeping 60s...")
                            time.sleep(60)
                        else:
                            print(f"      - Error page {page} (Attempt {attempt+1}/5): Status {m_res.status_code}")
                            time.sleep(5) 
                    except Exception as e:
                        print(f"      - Exception page {page} (Attempt {attempt+1}/5): {str(e)}")
                        time.sleep(10)
                    
                if not success:
                    print(f"      !!! Skipping {p_name} page {page} tras 5 intentos fallidos.")
                    break
                
                if not results:
                    break
                        
                print(f"      + Page {page} guardada: {len(results)} records")
                for r in results:
                    period = r.get('period', {})
                    date_val = None
                    if isinstance(period, dict):
                        dt_from = period.get('datetimeFrom')
                        if isinstance(dt_from, dict):
                            date_val = dt_from.get('utc')
                        else:
                            date_val = period.get('start') or period.get('utc')
                    
                    if not date_val:
                        date_val = r.get('date', {}).get('utc') or r.get('day')
                    
                    if date_val:
                        all_meas.append({
                            "station_name": location_name,
                            "station_id": location_id,
                            "sensor_id": s_id,
                            "parameter": p_name,
                            "value": r['value'],
                            "unit": u_name,
                            "datetime": date_val
                        })
                
                if len(results) < 1000:
                    break
                page += 1
    return all_meas

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch historical data from OpenAQ for Bogota.")
    parser.add_argument("--start", required=True, help="Start Date (ej. 2022-01-01T00:00:00Z)")
    parser.add_argument("--end", required=True, help="End Date (ej. 2022-12-31T23:59:59Z)")
    args = parser.parse_args()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(BASE_DIR, 'data', 'raw', 'bogota_pollution_hourly.csv')
    
    print(f"=== OpenAQ Data Extraction Segmentada ===")
    print(f"Start: {args.start}")
    print(f"End:   {args.end}")
    print(f"Archivo Maestro CSV: {output_path}\n")

    final_data_count = 0
    for s_id, s_name in STATIONS.items():
        print(f"------ Iniciando estación {s_name} (ID: {s_id}) ------")
        try:
            data = fetch_hourly_measurements(s_id, s_name, args.start, args.end)
            if data:
                df_temp = pd.DataFrame(data)
                # Verifica si el header debe existir o ya estaba creado
                header = not os.path.exists(output_path)
                df_temp.to_csv(output_path, mode='a', index=False, header=header)
                print(f"  --> \033[92m¡GUARDADO!\033[0m: Se unieron {len(data)} registros históricos de {s_name} al CSV maestro.\n")
                final_data_count += len(data)
            else:
                print(f"  --> VACÍO: La API no tiene datos de {s_name} en este año.\n")
        except KeyboardInterrupt:
            print("\n*** ¡Cancelado por el usuario con Ctrl+C! Cerrando limpiamente. ***")
            break
        except Exception as e:
            print(f"  !!! Error crítico fatal en estación {s_name}: {str(e)}\n")
            continue 
    
    if final_data_count > 0:
        print(f"\nSUCCESS! 🚀 Se extrajeron y acoplaron exitosamente a tu base: {final_data_count} filas.")
    else:
        print("\nFinalizado. No hubo datos biológicamente disponibles en esas fechas.")
