# scraper_betplay.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import time
import re
from playwright.sync_api import sync_playwright

# -----------------------
# CONFIGURACIÓN GOOGLE SHEETS
# -----------------------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = """${{ secrets.GOOGLE_CREDS }}"""  # Secreto GitHub
import json
from oauth2client.service_account import ServiceAccountCredentials

creds_json = os.environ["GOOGLE_CREDS"]
creds_dict = json.loads(creds_json)  # convertir string JSON en dict
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)

gc = gspread.authorize(creds)

# LIBROS
LIGAS_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNnC26J4ve/pubhtml"
BETPLAY_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSiLCx619Apna4bw3dlY-vcN4rzrhV5JOwb5tXujOcjZIP_F050Z4aJ3IytSCpU6GNqfeA6ymYGjATM/pubhtml"
DATOS_HORARIOS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSjU9YAn48_nYN7_eQxOIg7jz3jFxySgIgqdum0nFiu4CH88mCJpxIx-H1pfEIsZ7qGhHl57hxj1qwV/pubhtml"

# NOMBRES HOJAS
HOJA_LIGAS = "LIGA"
HOJA_BETPLAY = "BETPLAYULTIMO"
HOJA_BETPLAY_PREVIO = "BETPLAYPREVIO"
HOJA_FECHAS = "FECHAS"

# -----------------------
# FUNCIONES AUXILIARES
# -----------------------
def parse_fecha(texto_fecha):
    """Convierte 'hoy', 'mañana', 'lunes' a fecha dd/mm/yyyy"""
    texto_fecha = texto_fecha.lower()
    hoy = datetime.today()
    if "hoy" in texto_fecha:
        return hoy.strftime("%d/%m/%Y")
    elif "mañana" in texto_fecha:
        fecha = hoy + timedelta(days=1)
        return fecha.strftime("%d/%m/%Y")
    else:
        # intenta extraer dd/mm/yyyy de texto
        m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", texto_fecha)
        if m:
            return f"{int(m.group(1)):02d}/{int(m.group(2)):02d}/{m.group(3)}"
        else:
            return ""  # si no se reconoce

def parse_hora(texto_hora):
    """Convierte hora a formato 24h hh:mm"""
    texto_hora = texto_hora.strip()
    # ejemplo simple, puede mejorarse según necesidad
    m = re.match(r"(\d{1,2}):(\d{2})", texto_hora)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"
    else:
        return ""

# -----------------------
# LEER LIGAS ACTIVAS
# -----------------------
sh_ligas = gc.open_by_url(LIGAS_SHEET_URL)
worksheet_ligas = sh_ligas.worksheet(HOJA_LIGAS)
all_ligas = worksheet_ligas.get_all_records()  # lista de dicts
ligas_activas = [(row["PAIS"], row["LIGA"], row["BETPLAY"]) for row in all_ligas if row["ENCENDIDO"]]

print(f"📚 {len(ligas_activas)} ligas activas encontradas.")

# -----------------------
# MOVER DATOS ANTERIORES BETPLAY A BETPLAYPREVIO
# -----------------------
sh_betplay = gc.open_by_url(BETPLAY_SHEET_URL)
ws_ultimo = sh_betplay.worksheet(HOJA_BETPLAY)
ws_previo = sh_betplay.worksheet(HOJA_BETPLAY_PREVIO)

# copiar todo de BETPLAYULTIMO a BETPLAYPREVIO
ws_previo.clear()
ws_previo.update(ws_ultimo.get_all_values())

# limpiar BETPLAYULTIMO para llenarlo con nuevos datos
ws_ultimo.clear()
ws_ultimo.append_row(["PAIS","LIGA","DIA","HORA","LOCAL","VISITANTE","L","X","V","LIMITE GOL","C MAS","C MENOS"])

# -----------------------
# EXTRAER DATOS CON PLAYWRIGHT
# -----------------------
total_partidos = 0
partidos_data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for pais, liga, url in ligas_activas:
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            items = page.query_selector_all("li.KambiBC-sandwich-filter__event-list-item")
            if not items:
                print(f"⚠️ No hay partidos en {liga}")
                page.close()
                continue

            for item in items:
                equipos = item.query_selector_all("div.KambiBC-event-participants__name-participant-name")
                local = equipos[0].inner_text().strip() if len(equipos)>0 else ""
                visitante = equipos[1].inner_text().strip() if len(equipos)>1 else ""

                fecha_span = item.query_selector("span.KambiBC-event-item__start-time--date")
                hora_span = item.query_selector("span.KambiBC-event-item__start-time--time")
                dia = parse_fecha(fecha_span.inner_text().strip() if fecha_span else "")
                hora = parse_hora(hora_span.inner_text().strip() if hora_span else "")

                cuotas = item.query_selector_all("div.KambiBC-bet-offer--onecrosstwo button.KambiBC-betty-outcome")
                c1 = cuotas[0].inner_text().strip() if len(cuotas)>0 else ""
                cx = cuotas[1].inner_text().strip() if len(cuotas)>1 else ""
                c2 = cuotas[2].inner_text().strip() if len(cuotas)>2 else ""
                lim_gol = cuotas[3].inner_text().strip() if len(cuotas)>3 else ""
                c_mas = cuotas[4].inner_text().strip() if len(cuotas)>4 else ""
                c_menos = cuotas[5].inner_text().strip() if len(cuotas)>5 else ""

                row = [pais, liga, dia, hora, local, visitante, c1, cx, c2, lim_gol, c_mas, c_menos]
                partidos_data.append(row)
                total_partidos += 1

            page.close()
            print(f"✅ {len(items)} partidos extraídos de {liga}")

        except Exception as e:
            print(f"❌ Error en {liga}: {e}")
            page.close()
            continue

    browser.close()

# -----------------------
# GUARDAR DATOS NUEVOS EN BETPLAYULTIMO
# -----------------------
if partidos_data:
    for row in partidos_data:
        ws_ultimo.append_row(row)
    print(f"📊 {total_partidos} partidos guardados en BETPLAYULTIMO.")
else:
    print("⚠️ No se extrajo ningún partido.")

# -----------------------
# ACTUALIZAR NP BETPLAY EN LIGAS
# -----------------------
for idx, row in enumerate(all_ligas, start=2):
    liga = row["LIGA"]
    np_val = sum(1 for r in partidos_data if r[1] == liga)
    ws_ligas.update_cell(idx, 4, np_val)  # columna 4 = NP BETPLAY

# -----------------------
# ACTUALIZAR HOJA FECHAS
# -----------------------
sh_horarios = gc.open_by_url(DATOS_HORARIOS_URL)
ws_fechas = sh_horarios.worksheet(HOJA_FECHAS)

# mover ultima a previa
ultima_fila = ws_fechas.row_values(2)
if ultima_fila:
    ws_fechas.update("B2", ultima_fila[3])  # NP PREVIA
    ws_fechas.update("A2", ultima_fila[2])  # FECHA PREVIA

# actualizar ultima ejecución
ws_fechas.update("C2", datetime.now().strftime("%d/%m/%Y %H:%M"))  # FECHA ULTIMA
ws_fechas.update("D2", total_partidos)  # NP ULTIMA

print(f"\n⏱️ Scraper finalizado. Total partidos extraídos: {total_partidos}")
