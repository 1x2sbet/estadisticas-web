import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import os
import json

# ==============================
# CONFIGURACIÓN
# ==============================

URL_LIGAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNnC26J4ve/pub?output=csv"
URL_BETPLAY = "https://docs.google.com/spreadsheets/d/1fRLO4dnVoLh_wyBTZIcJsNFUKnH9SJuxJAvRuaIUpTg/edit?usp=sharing"

HOJA_ULTIMO = "BETPLAYULTIMO"
HOJA_PREVIO = "BETPLAYPREVIO"
HOJA_NP = "LIGAS"
HOJA_FECHAS = "FECHAS"

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
# LEER LIGAS (CON FILA REAL)
# ==============================

def leer_ligas():
    df = pd.read_csv(URL_LIGAS_CSV)
    df.columns = [c.strip().upper() for c in df.columns]

    df["FILA_REAL"] = df.index + 2
    return df

# ==============================
# SCRAPER (TU LÓGICA REAL VA AQUÍ)
# ==============================

def extraer_partidos(url):
    # ESTA FUNCIÓN DEBE SER TU SCRAPER REAL
    return ["PARTIDO 1", "PARTIDO 2"]

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
# ACTUALIZAR / LIMPIAR NP BETPLAY
# ==============================

def actualizar_np(ligas_df, np_dict):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_NP)

    headers = ws.row_values(1)
    col_np = headers.index("NP BETPLAY") + 1

    updates = []

    for _, row in ligas_df.iterrows():
        fila = int(row["FILA_REAL"])

        if row["ENCENDIDO"] is True:
            np_val = np_dict.get(row["BETPLAY"], 0)
        else:
            np_val = ""

        updates.append({
            "range": gspread.utils.rowcol_to_a1(fila, col_np),
            "values": [[np_val]]
        })

    ws.batch_update(updates)

# ==============================
# ACTUALIZAR FECHAS
# ==============================

def actualizar_fechas(np_total):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_FECHAS)

    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    valores = ws.col_values(2)

    fecha_previa = valores[3] if len(valores) > 3 else ""
    np_previa = valores[4] if len(valores) > 4 else ""

    ws.update("B2:B5", [
        [fecha_previa],
        [np_previa],
        [hoy],
        [np_total]
    ])

# ==============================
# MAIN
# ==============================

def main():
    print("📚 Leyendo ligas...")
    ligas = leer_ligas()

    todos_los_partidos = []
    np_por_liga = {}

    for _, row in ligas.iterrows():
        if row["ENCENDIDO"] is True:
            print(f"Extrayendo {row['LIGA']}...")
            partidos = extraer_partidos(row["BETPLAY"])
            todos_los_partidos.extend(partidos)
            np_por_liga[row["BETPLAY"]] = len(partidos)

    print("💾 Respaldando BETPLAYULTIMO...")
    respaldar_betplay()

    print("💾 Guardando partidos...")
    guardar_partidos(todos_los_partidos)

    print("🔢 Actualizando NP BETPLAY...")
    actualizar_np(ligas, np_por_liga)

    print("📅 Actualizando FECHAS...")
    actualizar_fechas(len(todos_los_partidos))

    print("✅ BETPLAY actualizado correctamente")

if __name__ == "__main__":
    main()
