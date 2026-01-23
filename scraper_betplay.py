import os
import json
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# =========================================================
# CONFIGURACIÓN
# =========================================================

# LECTURA DE LIGAS (CSV PÚBLICO)
URL_LIGAS_CSV = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNnC26J4ve"
    "/pub?output=csv"
)

# LIBRO BETPLAY (GUARDADO)
URL_BETPLAY = "https://docs.google.com/spreadsheets/d/1fRLO4dnVoLh_wyBTZIcJsNFUKnH9SJuxJAvRuaIUpTg/edit"

HOJA_ULTIMO = "BETPLAYULTIMO"
HOJA_PREVIO = "BETPLAYPREVIO"
HOJA_NP = "NP"
HOJA_FECHAS = "FECHAS"

# =========================================================
# AUTENTICACIÓN GOOGLE (GITHUB ACTIONS)
# =========================================================

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
gc = gspread.authorize(creds)

# =========================================================
# UTILIDADES FECHA / HORA
# =========================================================

def convertir_fecha(texto):
    hoy = datetime.now().date()
    texto = texto.lower().strip()

    if texto == "hoy":
        fecha = hoy
    elif texto == "mañana":
        fecha = hoy + timedelta(days=1)
    else:
        try:
            fecha = datetime.strptime(texto, "%d/%m/%Y").date()
        except:
            fecha = hoy

    return fecha.strftime("%d/%m/%Y")

# =========================================================
# LEER LIGAS ACTIVAS
# =========================================================

def leer_ligas():
    df = pd.read_csv(URL_LIGAS_CSV)
    df.columns = [c.strip().upper() for c in df.columns]

    df = df[df["ENCENDIDO"] == True]
    return df.reset_index(drop=True)

# =========================================================
# SCRAPER REAL (AQUÍ VA TU PLAYWRIGHT)
# =========================================================

def extraer_partidos(url, liga):
    """
    REEMPLAZA ESTA FUNCIÓN CON TU SCRAPER REAL
    Debe devolver lista de dict con las columnas finales
    """

    hoy = datetime.now().strftime("%d/%m/%Y")

    return [
        {
            "PAIS": "COLOMBIA",
            "LIGA": liga,
            "DIA": hoy,
            "HORA": "14:00",
            "LOCAL": "Equipo A",
            "VISITANTE": "Equipo B",
            "L": "",
            "X": "",
            "V": "",
            "LIMITE GOL": "",
            "C MAS": "",
            "C MENOS": ""
        }
    ]

# =========================================================
# RESPALDAR BETPLAYULTIMO → BETPLAYPREVIO
# =========================================================

def respaldar_betplay():
    sh = gc.open_by_url(URL_BETPLAY)
    ws_ultimo = sh.worksheet(HOJA_ULTIMO)
    ws_previo = sh.worksheet(HOJA_PREVIO)

    data = ws_ultimo.get_all_values()
    ws_previo.clear()

    if data:
        ws_previo.update(data)

# =========================================================
# GUARDAR BETPLAYULTIMO
# =========================================================

def guardar_betplay(df):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_ULTIMO)

    ws.clear()
    ws.update([df.columns.tolist()] + df.values.tolist())

# =========================================================
# ACTUALIZAR NP BETPLAY
# =========================================================

def actualizar_np(np_por_liga):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_NP)

    headers = ws.row_values(1)
    col_np = headers.index("NP BETPLAY") + 1

    updates = []
    for i, np_val in enumerate(np_por_liga, start=2):
        updates.append({
            "range": gspread.utils.rowcol_to_a1(i, col_np),
            "values": [[np_val]]
        })

    ws.batch_update(updates)

# =========================================================
# ACTUALIZAR FECHAS
# =========================================================

def actualizar_fechas(np_total):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_FECHAS)

    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    valores = ws.col_values(2)

    fecha_previa = valores[3] if len(valores) > 3 else ""
    np_previa = valores[4] if len(valores) > 4 else ""

    ws.update("B2:B5", [
        [fecha_previa],
        [np_previa],
        [ahora],
        [np_total]
    ])

# =========================================================
# MAIN
# =========================================================

def main():
    print("📚 Leyendo ligas activas...")
    ligas = leer_ligas()
    print(f"✅ {len(ligas)} ligas activas encontradas")

    todos = []
    np_ligas = []

    for _, row in ligas.iterrows():
        print(f"⚽ {row['LIGA']}")
        partidos = extraer_partidos(row["BETPLAY"], row["LIGA"])
        todos.extend(partidos)
        np_ligas.append(len(partidos))

    df_final = pd.DataFrame(todos)

    print("💾 Respaldando BETPLAYULTIMO → BETPLAYPREVIO")
    respaldar_betplay()

    print("💾 Guardando BETPLAYULTIMO")
    guardar_betplay(df_final)

    print("🔢 Actualizando NP BETPLAY")
    actualizar_np(np_ligas)

    print("📅 Actualizando FECHAS")
    actualizar_fechas(len(df_final))

    print("✅ SCRAPER BETPLAY FINALIZADO CORRECTAMENTE")

# =========================================================

if __name__ == "__main__":
    main()
