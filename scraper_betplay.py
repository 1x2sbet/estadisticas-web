# scraper_betplay.py
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re
from datetime import datetime, timedelta

# ------------------------------
# CONFIGURACIÓN GOOGLE SHEETS
# ------------------------------
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Leer el secreto de GitHub Actions
creds_json = os.environ["GOOGLE_CREDS"]
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
gc = gspread.authorize(creds)

# URLs de Google Sheets
URL_LIGAS = "https://docs.google.com/spreadsheets/d/2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNnC26J4ve/edit#gid=0"
URL_BETPLAY = "https://docs.google.com/spreadsheets/d/1fRLO4dnVoLh_wyBTZIcJsNFUKnH9SJuxJAvRuaIUpTg/edit#gid=0"
URL_DATOS_HORARIOS = "https://docs.google.com/spreadsheets/d/1Uwty-fiIWzodWywxk9DIyDU7n_27__bL8X-RADwesa8/edit#gid=0"

# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------

def leer_ligas():
    """Leer ligas activas desde Google Sheets"""
    df = pd.read_csv(URL_LIGAS)
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
        # intentar parsear fecha explícita, asumiendo formato dd/mm/yyyy
        try:
            fecha = datetime.strptime(fecha_texto, "%d/%m/%Y")
        except:
            fecha = hoy  # fallback
    # hora
    try:
        hora = datetime.strptime(hora_texto, "%H:%M").time()
    except:
        hora = datetime.strptime("00:00", "%H:%M").time()
    fecha_formato = fecha.strftime("%d/%m/%Y")
    hora_formato = hora.strftime("%H:%M")
    return fecha_formato, hora_formato

def actualizar_np_ligas(np_por_liga):
    """Actualiza la columna NP BETPLAY en la hoja LIGAS"""
    sheet = gc.open_by_url(URL_LIGAS).worksheet("LIGA")
    data = sheet.get_all_records()
    for idx, row in enumerate(data, start=2):
        liga = row.get('LIGA', '')
        valor_np = np_por_liga.get(liga, "")
        sheet.update_cell(idx, sheet.find("NP BETPLAY").col, valor_np)

def respaldar_betplay(sheet_name="BETPLAYULTIMO"):
    """Respalda BETPLAYULTIMO a BETPLAYPREVIO"""
    sh = gc.open_by_url(URL_BETPLAY)
    df_actual = pd.DataFrame(sh.worksheet(sheet_name).get_all_records())
    prev_sheet = sh.worksheet("BETPLAYPREVIO")
    prev_sheet.clear()
    prev_sheet.update([df_actual.columns.values.tolist()] + df_actual.values.tolist())

def actualizar_datos_horarios(np_total):
    """Actualiza hoja DATOS HORARIOS"""
    sh = gc.open_by_url(URL_DATOS_HORARIOS).worksheet("FECHAS")
    datos = sh.get_all_values()
    # mover última a previa
    sh.update_cell(2, 1, datos[1][2])  # FECHA PREVIA
    sh.update_cell(2, 2, datos[1][3])  # NP PREVIA
    # guardar nueva última
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    sh.update_cell(2, 3, now_str)       # FECHA ULTIMA
    sh.update_cell(2, 4, np_total)      # NP ULTIMA

# ------------------------------
# FUNCIÓN PRINCIPAL DEL SCRAPER
# ------------------------------
def main():
    print("📚 Leyendo ligas activas...")
    urls = leer_ligas()
    print(f"✅ {len(urls)} ligas activas encontradas.")

    # Aquí iría tu lógica de extracción con Playwright (o requests)
    # Por simplicidad, simulamos extracción
    resultados = []
    np_por_liga = {}

    for idx, row in urls.iterrows():
        liga = row['LIGA']
        link = row['BETPLAY']
        # Simular extracción
        print(f"Extrayendo partidos de {liga} ({link}) ...")
        cantidad = 5  # simulamos 5 partidos
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

    # Guardar respaldo de BETPLAYULTIMO
    print("💾 Respaldando BETPLAYULTIMO a BETPLAYPREVIO...")
    respaldar_betplay("BETPLAYULTIMO")

    # Guardar nuevos datos en BETPLAYULTIMO
    print("💾 Actualizando BETPLAYULTIMO...")
    sh = gc.open_by_url(URL_BETPLAY).worksheet("BETPLAYULTIMO")
    df_nuevo = pd.DataFrame(resultados)
    sh.clear()
    sh.update([df_nuevo.columns.values.tolist()] + df_nuevo.values.tolist())

    # Actualizar NP BETPLAY
    print("🔢 Actualizando NP BETPLAY...")
    actualizar_np_ligas(np_por_liga)

    # Actualizar DATOS HORARIOS
    print("⏱ Actualizando DATOS HORARIOS...")
    actualizar_datos_horarios(np_total=sum(np_por_liga.values()))

    print("✅ Scraper finalizado correctamente.")

# ------------------------------
# EJECUCIÓN
# ------------------------------
if __name__ == "__main__":
    main()
