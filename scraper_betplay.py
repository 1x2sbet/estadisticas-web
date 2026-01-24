import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import re
from playwright.sync_api import sync_playwright, TimeoutError
from zoneinfo import ZoneInfo

# ==============================
# CONFIGURACIÓN
# ==============================

URL_LIGAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNnC26J4ve/pub?output=csv"
URL_BETPLAY = "https://docs.google.com/spreadsheets/d/1fRLO4dnVoLh_wyBTZIcJsNFUKnH9SJuxJAvRuaIUpTg/edit?usp=sharing"

HOJA_ULTIMO = "BETPLAYULTIMO"
HOJA_PREVIO = "BETPLAYPREVIO"
HOJA_NP = "NP"
HOJA_FECHAS = "FECHAS"

TZ_BOGOTA = ZoneInfo("America/Bogota")

# ==============================
# AUTENTICACIÓN
# ==============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_json = json.loads(os.environ["GOOGLE_CREDS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc = gspread.authorize(creds)

# ==============================
# LEER LIGAS
# ==============================

def leer_ligas():
    df = pd.read_csv(URL_LIGAS_CSV)
    df.columns = [c.strip().upper() for c in df.columns]

    df["ENCENDIDO"] = df["ENCENDIDO"].astype(str).str.upper().isin(["TRUE", "1", "SI", "YES"])
    df["FILA_REAL"] = df.index + 2

    return df

# ==============================
# SCRAPER BETPLAY
# ==============================

def limpiar_cuota(txt):
    if not txt:
        return ""
    m = re.search(r"\d+(\.\d+)?", txt.replace(",", "."))
    return m.group(0) if m else ""

def extraer_partidos(page, pais, liga, url):
    partidos = []

    try:
        page.goto(url, timeout=60000)
        page.wait_for_selector(
            "li.KambiBC-sandwich-filter__event-list-item",
            timeout=30000
        )

        items = page.query_selector_all(
            "li.KambiBC-sandwich-filter__event-list-item"
        )

        hoy = datetime.now(TZ_BOGOTA).date()

        for p in items:
            try:
                equipos = p.query_selector_all(
                    "div.KambiBC-event-participants__name-participant-name"
                )
                if len(equipos) < 2:
                    continue

                local = equipos[0].inner_text().strip()
                visitante = equipos[1].inner_text().strip()

                fecha_span = p.query_selector("span.KambiBC-event-item__start-time--date")
                hora_span = p.query_selector("span.KambiBC-event-item__start-time--time")

                fecha_txt = fecha_span.inner_text().strip() if fecha_span else ""
                hora_txt = hora_span.inner_text().strip() if hora_span else ""

                if "HOY" in fecha_txt.upper():
                    fecha = hoy.strftime("%d/%m/%Y")
                elif "MAÑANA" in fecha_txt.upper():
                    fecha = (hoy + timedelta(days=1)).strftime("%d/%m/%Y")
                else:
                    fecha = fecha_txt

                cuotas = p.query_selector_all(
                    "div.KambiBC-bet-offer--onecrosstwo button.KambiBC-betty-outcome"
                )

                c1 = limpiar_cuota(cuotas[0].inner_text()) if len(cuotas) > 0 else ""
                cx = limpiar_cuota(cuotas[1].inner_text()) if len(cuotas) > 1 else ""
                c2 = limpiar_cuota(cuotas[2].inner_text()) if len(cuotas) > 2 else ""

                partidos.append([
                    pais, liga, fecha, hora_txt,
                    local, visitante,
                    c1, cx, c2,
                    "", "", ""
                ])

            except:
                continue

    except TimeoutError:
        pass

    return partidos

# ==============================
# RESPALDAR ULTIMO → PREVIO
# ==============================

def respaldar_betplay():
    sh = gc.open_by_url(URL_BETPLAY)
    ws_u = sh.worksheet(HOJA_ULTIMO)
    ws_p = sh.worksheet(HOJA_PREVIO)

    data = ws_u.get_all_values()
    ws_p.clear()
    if data:
        ws_p.update(data)

# ==============================
# GUARDAR PARTIDOS
# ==============================

def guardar_partidos(partidos):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_ULTIMO)

    ws.clear()
    ws.update([[
        "PAIS","LIGA","DIA","HORA","LOCAL","VISITANTE",
        "L","X","V","LIMITE GOL","C MAS","C MENOS"
    ]])

    if partidos:
        ws.update(partidos, "A2")

# ==============================
# ACTUALIZAR NP
# ==============================

def actualizar_np(ligas_df, np_dict):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_NP)

    headers = ws.row_values(1)
    if "NP BETPLAY" not in headers:
        return

    col_np = headers.index("NP BETPLAY") + 1
    updates = []

    for _, row in ligas_df.iterrows():
        fila = int(row["FILA_REAL"])
        val = np_dict.get(row["BETPLAY"], "") if row["ENCENDIDO"] else ""

        updates.append({
            "range": gspread.utils.rowcol_to_a1(fila, col_np),
            "values": [[val]]
        })

    if updates:
        ws.batch_update(updates)

# ==============================
# FECHAS
# ==============================

def actualizar_fechas(np_total):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_FECHAS)

    ahora = datetime.now(TZ_BOGOTA).strftime("%Y-%m-%d %H:%M:%S")
    valores = ws.col_values(2)

    fecha_previa = valores[3] if len(valores) > 3 else ""
    np_previa = valores[4] if len(valores) > 4 else ""

    ws.update("B2:B5", [
        [fecha_previa],
        [np_previa],
        [ahora],
        [np_total]
    ])

# ==============================
# MAIN
# ==============================

def main():
    ligas = leer_ligas()
    todos = []
    np_por_liga = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for _, row in ligas.iterrows():
            if not row["ENCENDIDO"]:
                continue

            page = context.new_page()
            partidos = extraer_partidos(
                page,
                row["PAIS"],
                row["LIGA"],
                row["BETPLAY"]
            )
            page.close()

            todos.extend(partidos)
            np_por_liga[row["BETPLAY"]] = len(partidos)

        browser.close()

    respaldar_betplay()
    guardar_partidos(todos)
    actualizar_np(ligas, np_por_liga)
    actualizar_fechas(len(todos))

    print(f"✅ BETPLAY actualizado correctamente | Partidos: {len(todos)}")

if __name__ == "__main__":
    main()
