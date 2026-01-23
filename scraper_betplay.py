from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# CONFIGURACIÓN GOOGLE SHEETS
# -----------------------------
# Credenciales JSON que creaste para tu cuenta de servicio
CREDENTIALS_FILE = "google_credentials.json"

# URLs publicados
URL_LIGAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNq26J4ve/pub?output=csv"
URL_BETPLAY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSiLCx619Apna4bw3dlY-vcN4rzrhV5JOwb5tXujOcjZIP_F050Z4aJ3IytSCpU6GNqfeA6ymYGjATM/pub?output=csv"
URL_DATOS_HORARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSjU9YAn48_nYN7_eQxOIg7jz3jFxySgIgqdum0nFiu4CH88mCJpxIx-H1pfEIsZ7qGhHl57hxj1qwV/pub?output=csv"

# Nombre de las hojas
HOJA_BETPLAYULTIMO = "BETPLAYULTIMO"
HOJA_BETPLAYPREVIO = "BETPLAYPREVIO"
HOJA_LIGA = "LIGA"
HOJA_DATOS_FECHAS = "FECHAS"

# -----------------------------
# GOOGLE SHEETS AUTH
# -----------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
gc = gspread.authorize(creds)

# Abrir hojas
sh_betplay = gc.open_by_url(URL_BETPLAY)
ws_ultimo = sh_betplay.worksheet(HOJA_BETPLAYULTIMO)
ws_previo = sh_betplay.worksheet(HOJA_BETPLAYPREVIO)

sh_ligas = gc.open_by_url(URL_LIGAS)
ws_ligas = sh_ligas.worksheet(HOJA_LIGA)

sh_horarios = gc.open_by_url(URL_DATOS_HORARIOS)
ws_fechas = sh_horarios.worksheet(HOJA_DATOS_FECHAS)

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------
def parse_fecha(fecha_str):
    """Convierte 'hoy', 'mañana', 'lunes', o dd/mm/yyyy a dd/mm/yyyy"""
    fecha_str = fecha_str.strip().lower()
    hoy = datetime.now()
    dias_semana = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]

    if fecha_str == "hoy":
        return hoy.strftime("%d/%m/%Y")
    elif fecha_str == "mañana":
        return (hoy + timedelta(days=1)).strftime("%d/%m/%Y")
    elif fecha_str in dias_semana:
        diff = (dias_semana.index(fecha_str) - hoy.weekday() + 7) % 7
        if diff == 0:
            diff = 7
        return (hoy + timedelta(days=diff)).strftime("%d/%m/%Y")
    else:
        try:
            dt = datetime.strptime(fecha_str, "%d/%m/%Y")
            return dt.strftime("%d/%m/%Y")
        except:
            return fecha_str

def parse_hora(hora_str):
    """Convierte hora a formato 24h"""
    hora_str = hora_str.strip()
    try:
        dt = datetime.strptime(hora_str, "%I:%M %p")
        return dt.strftime("%H:%M")
    except:
        return hora_str

# -----------------------------
# LEER LIGAS ACTIVAS
# -----------------------------
df_ligas = pd.read_csv(URL_LIGAS)
df_ligas = df_ligas[df_ligas["ENCENDIDO"] == True]  # solo activas
urls = list(zip(df_ligas["LIGA"], df_ligas["BETPLAY"], df_ligas["PAIS"]))

print(f"📚 {len(urls)} ligas activas para procesar.")

# -----------------------------
# GUARDAR BETPLAYULTIMO EN BETPLAYPREVIO
# -----------------------------
betplay_ultimo = ws_ultimo.get_all_values()
if len(betplay_ultimo) > 1:
    ws_previo.clear()
    ws_previo.update("A1", betplay_ultimo)  # copia todo el contenido

# -----------------------------
# EXTRAER PARTIDOS
# -----------------------------
all_results = []

def extraer_partidos(page, liga, url, pais):
    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(9000)

        items = page.query_selector_all("li.KambiBC-sandwich-filter__event-list-item")
        partidos = []

        for p in items:
            equipos = p.query_selector_all("div.KambiBC-event-participants__name-participant-name")
            local = equipos[0].inner_text().strip() if len(equipos) > 0 else ""
            visitante = equipos[1].inner_text().strip() if len(equipos) > 1 else ""

            fecha_span = p.query_selector("span.KambiBC-event-item__start-time--date")
            hora_span = p.query_selector("span.KambiBC-event-item__start-time--time")
            fecha = parse_fecha(fecha_span.inner_text().strip()) if fecha_span else ""
            hora = parse_hora(hora_span.inner_text().strip()) if hora_span else ""

            cuotas = p.query_selector_all("div.KambiBC-bet-offer--onecrosstwo button.KambiBC-betty-outcome")
            c1 = cuotas[0].inner_text().strip() if len(cuotas) > 0 else ""
            cx = cuotas[1].inner_text().strip() if len(cuotas) > 1 else ""
            c2 = cuotas[2].inner_text().strip() if len(cuotas) > 2 else ""
            lim_gol = ""  # si quieres calcularlo después
            c_mas = ""
            c_menos = ""

            partidos.append({
                "PAIS": pais,
                "LIGA": liga,
                "DIA": fecha,
                "HORA": hora,
                "LOCAL": local,
                "VISITANTE": visitante,
                "L": c1,
                "X": cx,
                "V": c2,
                "LIMITE GOL": lim_gol,
                "C MAS": c_mas,
                "C MENOS": c_menos
            })

        print(f"✅ {len(partidos)} partidos extraídos de {liga}")
        return partidos
    except Exception as e:
        print(f"❌ Error en {liga}: {e}")
        return []

# -----------------------------
# INICIAR PLAYWRIGHT
# -----------------------------
start_time = time.time()
total_partidos = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for liga, url, pais in urls:
        partidos = extraer_partidos(page, liga, url, pais)
        all_results.extend(partidos)
        total_partidos += len(partidos)

    browser.close()

# -----------------------------
# GUARDAR DATOS EN BETPLAYULTIMO
# -----------------------------
if all_results:
    df = pd.DataFrame(all_results)
    ws_ultimo.clear()
    ws_ultimo.update([df.columns.tolist()] + df.values.tolist())
    print(f"💾 Datos guardados en BETPLAYULTIMO ({len(all_results)} partidos)")
else:
    print("⚠️ No se extrajo ningún partido")

# -----------------------------
# ACTUALIZAR NP BETPLAY EN LIGAS
# -----------------------------
for idx, row in df_ligas.iterrows():
    liga = row["LIGA"]
    np_value = len([p for p in all_results if p["LIGA"] == liga])
    cell = ws_ligas.find(liga)
    if cell:
        ws_ligas.update_cell(cell.row, ws_ligas.find("NP BETPLAY").col, np_value)

# -----------------------------
# ACTUALIZAR DATOS HORARIOS
# -----------------------------
# Leer primera columna (DATOS) y formar matriz
fechas_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
np_ultima = total_partidos

# Leer fila existente
matriz = ws_fechas.get("B2:E2")  # columnas B a E fila 2
if matriz:
    fecha_previa, np_previa, _, _ = matriz[0]
else:
    fecha_previa, np_previa = "", 0

# Actualizar
ws_fechas.update("B2:E2", [[fecha_previa, np_previa, fechas_actual, np_ultima]])

print(f"\n⏱️ Tiempo total ejecución: {time.time() - start_time:.2f}s")
print(f"📊 Total partidos extraídos: {total_partidos}")
