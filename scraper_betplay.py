# scraper_betplay.py
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re
from datetime import datetime, timedelta
import time

# ------------------------------
# CONFIGURACIÓN GOOGLE SHEETS
# ------------------------------
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Leer el secreto de GitHub Actions
creds_json = os.environ["GOOGLE_CREDS"]
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
gc = gspread.authorize(creds)

# URLs de Google Sheets (ya con permisos de edición)
URL_LIGAS_EDIT = "https://docs.google.com/spreadsheets/d/12Cu-9JFawygQ8G7kIR0ai3EII09s21Gz3HguS1Botm4/edit"
URL_BETPLAY = "https://docs.google.com/spreadsheets/d/12Cu-9JFawygQ8G7kIR0ai3EII09s21Gz3HguS1Botm4/edit"
URL_DATOS_HORARIOS = "https://docs.google.com/spreadsheets/d/12Cu-9JFawygQ8G7kIR0ai3EII09s21Gz3HguS1Botm4/edit"

# CSV de ligas activas
URL_LIGAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNnC26J4ve/pub?output=csv"

# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------

def leer_ligas():
    """Leer ligas activas desde Google Sheets CSV"""
    df = pd.read_csv(URL_LIGAS_CSV)
    df.columns = [c.strip().upper() for c in df.columns]
    df = df[df['ENCENDIDO'] == True]
    urls = df[['LIGA', 'BETPLAY']].dropna()
    return urls

def formatear_fecha_hora(fecha_texto, hora_texto):
    """Convierte fecha/hora a formato dd/mm/yyyy y HH:MM"""
    fecha_texto = fecha_texto.lower().strip()
    hoy = datetime.today()

    if fecha_texto in ['hoy']:
        fecha = hoy
    elif fecha_texto in ['mañana']:
        fecha = hoy + timedelta(days=1)
    else:
        try:
            fecha = datetime.strptime(fecha_texto, "%d/%m/%Y")
        except:
            fecha = hoy
    try:
        hora = datetime.strptime(hora_texto, "%H:%M").time()
    except:
        hora = datetime.strptime("00:00", "%H:%M").time()
    fecha_formato = fecha.strftime("%d/%m/%Y")
    hora_formato = hora.strftime("%H:%M")
    return fecha_formato, hora_formato

def actualizar_np_ligas(np_por_liga):
    """Actualiza la columna NP BETPLAY en la hoja LIGAS usando batch update"""
    sheet = gc.open_by_url(URL_LIGAS_EDIT).worksheet("LIGA")
    data = sheet.get_all_records()
    header = sheet.row_values(1)
    col_np = header.index("NP BETPLAY") + 1

    # Preparar lista de celdas a actualizar
    updates = []
    for idx, row in enumerate(data, start=2):
        liga = row.get('LIGA', '')
        valor_np = np_por_liga.get(liga, "")
        updates.append({
            "range": gspread.utils.rowcol_to_a1(idx, col_np),
            "values": [[valor_np]]
        })
    # Actualizar en bloque
    if updates:
        sheet.batch_update(updates)

def respaldar_betplay(sheet_name="BETPLAYULTIMO"):
    """Respalda BETPLAYULTIMO a BETPLAYPREVIO usando batch update"""
    sh = gc.open_by_url(URL_BETPLAY)
    df_actual = pd.DataFrame(sh.worksheet(sheet_name).get_all_records())
    prev_sheet = sh.worksheet("BETPLAYPREVIO")
    prev_sheet.clear()
    if not df_actual.empty:
        prev_sheet.update([df_actual.columns.values.tolist()] + df_actual.values.tolist())

def actualizar_datos_horarios(np_total):
    """Actualiza hoja DATOS HORARIOS usando batch update"""
    sh = gc.open_by_url(URL_DATOS_HORARIOS).worksheet("FECHAS")
    datos = sh.get_all_values()
    # mover última a previa
    prev_vals = [[datos[1][2], datos[1][3]]]  # FECHA ULTIMA, NP ULTIMA
    sh.update('A2:B2', prev_vals)
    # guardar nueva última
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    sh.update('C2:D2', [[now_str, np_total]])

# ------------------------------
# FUNCIÓN PRINCIPAL DEL SCRAPER
# ------------------------------
def main():
    print("📚 Leyendo ligas activas...")
    urls = leer_ligas()
    print(f"✅ {len(urls)} ligas activas encontradas.")

    # Aquí iría tu lógica de extracción con Playwright
    resultados = []
    np_por_liga = {}

    for idx, row in urls.iterrows():
        liga = row['LIGA']
        link = row['BETPLAY']
        print(f"Extrayendo partidos de {liga} ({link}) ...")
        cantidad = 5
        np_por_liga[liga] = cantidad
        for i in range(cantidad):
            resultados.append({
                "PAIS": "Colombia",
                "LIGA": liga,
                "DIA": datetime.today().strftime("%d/%m/%Y"),
                "HORA": "15:00",
                "LOCAL": f"Local {i+1}",
                "VISITANTE": f"Visitante {i+1}",
                "L": "",
                "X": "",
                "V": "",
                "LIMITE GOL": "",
                "C MAS": "",
                "C MENOS": ""
            })

    print("💾 Respaldando BETPLAYULTIMO a BETPLAYPREVIO...")
    respaldar_betplay("BETPLAYULTIMO")

    print("💾 Actualizando BETPLAYULTIMO...")
    sh = gc.open_by_url(URL_BETPLAY).worksheet("BETPLAYULTIMO")
    df_nuevo = pd.DataFrame(resultados)
    sh.clear()
    if not df_nuevo.empty:
        sh.update([df_nuevo.columns.values.tolist()] + df_nuevo.values.tolist())

    print("🔢 Actualizando NP BETPLAY...")
    actualizar_np_ligas(np_por_liga)

    print("⏱ Actualizando DATOS HORARIOS...")
    actualizar_datos_horarios(np_total=sum(np_por_liga.values()))

    print("✅ Scraper finalizado correctamente.")

# ------------------------------
# EJECUCIÓN
# ------------------------------
if __name__ == "__main__":
    main()
