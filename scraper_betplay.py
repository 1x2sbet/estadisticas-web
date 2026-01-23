from playwright.sync_api import sync_playwright
import pandas as pd
import time
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------
# GOOGLE SHEETS SETUP
# -----------------------
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

CREDS = ServiceAccountCredentials.from_json_keyfile_name(
    "google_credentials.json", SCOPE
)

gc = gspread.authorize(CREDS)

# -----------------------
# DOCUMENTOS
# -----------------------
LIGAS_SHEET = gc.open_by_key("12Cu-9JFawygQ8G7kIR0ai3EII09s21Gz3HguS1Botm4")
DATA_SHEET = gc.open_by_key("1fRLO4dnVoLh_wyBTZIcJsNFUKnH9SJuxJAvRuaIUpTg")
HORARIOS_SHEET = gc.open_by_key("1Uwty-fiIWzodWywxk9DIyDU7n_27__bL8X-RADwesa8")

# -----------------------
# LEER LIGAS ACTIVAS
# -----------------------
def leer_ligas_activas():
    ws = LIGAS_SHEET.worksheet("LIGA")
    df = pd.DataFrame(ws.get_all_records())

    df.columns = df.columns.str.upper()

    activas = df[
        (df["ENCENDIDO"] == True) &
        (df["BETPLAY"].str.startswith("http"))
    ]

    return activas[["PAIS", "LIGA", "BETPLAY"]]

# -----------------------
# FECHA DESDE TEXTO
# -----------------------
def parse_fecha(texto):
    hoy = datetime.now().date()

    texto = texto.lower()
    if "hoy" in texto:
        return hoy
    if "mañana" in texto:
        return hoy + timedelta(days=1)

    dias = {
        "lunes": 0, "martes": 1, "miércoles": 2,
        "jueves": 3, "viernes": 4,
        "sábado": 5, "domingo": 6
    }

    for d, v in dias.items():
        if d in texto:
            delta = (v - hoy.weekday()) % 7
            return hoy + timedelta(days=delta)

    return hoy

# -----------------------
# SCRAPER BETPLAY
# -----------------------
def extraer_liga(page, pais, liga, url):
    page.goto(url, timeout=60000)
    page.wait_for_timeout(8000)

    partidos = []

    items = page.query_selector_all("li.KambiBC-sandwich-filter__event-list-item")

    for p in items:
        equipos = p.query_selector_all("div.KambiBC-event-participants__name-participant-name")
        cuotas = p.query_selector_all("button.KambiBC-betty-outcome")

        fecha_txt = p.inner_text()

        fecha = parse_fecha(fecha_txt)
        hora = p.query_selector("span.KambiBC-event-item__start-time--time")

        partidos.append([
            pais,
            liga,
            fecha.strftime("%d/%m/%Y"),
            hora.inner_text() if hora else "",
            equipos[0].inner_text(),
            equipos[1].inner_text(),
            cuotas[0].inner_text(),
            cuotas[1].inner_text(),
            cuotas[2].inner_text(),
            "", "", ""
        ])

    return partidos

# -----------------------
# PROGRAMA PRINCIPAL
# -----------------------
def main():

    ligas = leer_ligas_activas()

    ws_ultimo = DATA_SHEET.worksheet("BETPLAYULTIMO")
    ws_previo = DATA_SHEET.worksheet("BETPLAYPREVIO")

    # Guardar histórico
    ws_previo.clear()
    ws_previo.update(ws_ultimo.get_all_values())

    resultados = []
    total_np = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for _, row in ligas.iterrows():
            datos = extraer_liga(page, row["PAIS"], row["LIGA"], row["BETPLAY"])
            total_np += len(datos)
            resultados.extend(datos)

        browser.close()

    ws_ultimo.clear()
    ws_ultimo.update(
        [["PAIS","LIGA","DIA","HORA","LOCAL","VISITANTE","L","X","V","LIMITE GOL","C MAS","C MENOS"]]
        + resultados
    )

    # Actualizar control horario
    ws_fechas = HORARIOS_SHEET.worksheet("FECHAS")
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    ws_fechas.update("B3", ws_fechas.acell("B5").value)
    ws_fechas.update("B4", ws_fechas.acell("B6").value)

    ws_fechas.update("B5", ahora)
    ws_fechas.update("B6", total_np)

if __name__ == "__main__":
    main()
