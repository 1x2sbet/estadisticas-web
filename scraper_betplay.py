import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# ==============================
# CONFIGURACIÓN
# ==============================

URL_LIGAS = "https://docs.google.com/spreadsheets/d/TU_ID_LIGAS"
URL_BETPLAY = "https://docs.google.com/spreadsheets/d/TU_ID_BETPLAY"

HOJA_LIGAS = "LIGAS"

HOJA_ULTIMO = "BETPLAYULTIMO"
HOJA_PREVIO = "BETPLAYPREVIO"
HOJA_NP = "NP"
HOJA_FECHAS = "FECHAS"

# ==============================
# AUTENTICACIÓN
# ==============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
gc = gspread.authorize(creds)

# ==============================
# LECTURA DE LIGAS
# ==============================

def leer_ligas():
    sh = gc.open_by_url(URL_LIGAS)
    ws = sh.worksheet(HOJA_LIGAS)
    df = pd.DataFrame(ws.get_all_records())

    df = df[df["ACTIVA"] == 1]
    return df.reset_index(drop=True)

# ==============================
# SCRAPER (NO CAMBIES TU LÓGICA)
# ==============================

def extraer_partidos(url):
    """
    ESTA FUNCIÓN DEBE SER TU SCRAPER REAL
    Debe retornar una lista de partidos
    """
    # EJEMPLO
    partidos = ["PARTIDO 1", "PARTIDO 2"]
    return partidos

# ==============================
# RESPALDAR ULTIMO → PREVIO
# ==============================

def respaldar_betplay():
    sh = gc.open_by_url(URL_BETPLAY)

    ws_ultimo = sh.worksheet(HOJA_ULTIMO)
    ws_previo = sh.worksheet(HOJA_PREVIO)

    data = ws_ultimo.get_all_values()

    ws_previo.clear()
    if data:
        ws_previo.update(data)

# ==============================
# GUARDAR PARTIDOS
# ==============================

def guardar_partidos(todos_los_partidos):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_ULTIMO)

    ws.clear()
    ws.update([["PARTIDOS"]])

    if todos_los_partidos:
        ws.update([[p] for p in todos_los_partidos], "A2")

# ==============================
# ACTUALIZAR NP
# ==============================

def actualizar_np(np_por_liga):
    sh = gc.open_by_url(URL_BETPLAY)
    ws = sh.worksheet(HOJA_NP)

    encabezados = ws.row_values(1)
    col_np = encabezados.index("NP BETPLAY") + 1

    updates = []
    for i, np_val in enumerate(np_por_liga, start=2):
        updates.append({
            "range": gspread.utils.rowcol_to_a1(i, col_np),
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

    fecha_ultima = hoy
    np_ultima = np_total

    fecha_previa = valores[3] if len(valores) > 3 else ""
    np_previa = valores[4] if len(valores) > 4 else ""

    ws.update("B2:B5", [
        [fecha_previa],
        [np_previa],
        [fecha_ultima],
        [np_ultima]
    ])

# ==============================
# MAIN
# ==============================

def main():
    print("📚 Leyendo ligas activas...")
    ligas = leer_ligas()
    print(f"✅ {len(ligas)} ligas activas encontradas.")

    todos_los_partidos = []
    np_por_liga = []

    for _, row in ligas.iterrows():
        print(f"Extrayendo partidos de {row['LIGA']} ({row['URL']}) ...")
        partidos = extraer_partidos(row["URL"])

        todos_los_partidos.extend(partidos)
        np_por_liga.append(len(partidos))

    print("💾 Respaldando BETPLAYULTIMO a BETPLAYPREVIO...")
    respaldar_betplay()

    print("💾 Actualizando BETPLAYULTIMO...")
    guardar_partidos(todos_los_partidos)

    print("🔢 Actualizando NP BETPLAY...")
    actualizar_np(np_por_liga)

    print("📅 Actualizando FECHAS...")
    actualizar_fechas(len(todos_los_partidos))

    print("✅ BETPLAY actualizado correctamente")

if __name__ == "__main__":
    main()
