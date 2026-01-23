import streamlit as st
import pandas as pd

# ---------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------
st.set_page_config(
    page_title="1X2sBet",
    page_icon="⚽",
    layout="wide"
)

# ---------------------------------
# GOOGLE SHEETS (BASE DE DATOS)
# ---------------------------------
LIGAS_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vRV_Y8liM7yoZOX-wo6xQraDds-S8rcwFEbit_4NqAaH8mz1I6kAG7z1pF67YFrej-MMfsNnC26J4ve/"
    "pub?output=csv"
)

# ---------------------------------
# MENÚ LATERAL
# ---------------------------------
st.sidebar.title("⚽ 1X2sBet")

menu = st.sidebar.radio(
    "Navegación",
    [
        "🏠 Inicio",
        "🏦 Casas de Apuestas",
        "🏆 Ligas",
        "📊 Análisis",
        "🧮 Herramientas",
        "💼 Gestión"
    ]
)

# ---------------------------------
# INICIO
# ---------------------------------
if menu == "🏠 Inicio":
    st.title("📊 Plataforma de Análisis Estadístico")
    st.write(
        """
        Bienvenido a **1X2sBet**.  
        Plataforma de análisis estadístico deportivo basada en datos
        generados automáticamente con Python.
        """
    )

# ---------------------------------
# CASAS DE APUESTAS
# ---------------------------------
elif menu == "🏦 Casas de Apuestas":

    st.title("🏦 Casas de Apuestas Legales en Colombia")

    casas = {
        "BETANO": "assets/logos/betano.png",
        "BETPLAY": "assets/logos/betplay.png",
        "BETSSON": "assets/logos/betsson.png",
        "BINGOCASINOS": "assets/logos/bingocasinos.png",
        "BWIN": "assets/logos/bwin.png",
        "CODERE": "assets/logos/codere.png",
        "LUCKIA": "assets/logos/luckia.png",
        "RIVALO": "assets/logos/rivalo.png",
        "RUSHBET": "assets/logos/rushbet.png",
        "SPORTIUM": "assets/logos/sportium.png",
        "STAKE": "assets/logos/stake.png",
        "WPLAY": "assets/logos/wplay.png",
        "YAJUEGO": "assets/logos/yajuego.png",
        "ZAMBA": "assets/logos/zamba.png",
    }

    if "casas_activas" not in st.session_state:
        st.session_state.casas_activas = {c: True for c in casas}

    for casa, logo in casas.items():
        col1, col2 = st.columns([1, 6])

        with col1:
            st.image(logo, width=35)

        with col2:
            st.session_state.casas_activas[casa] = st.checkbox(
                casa,
                value=st.session_state.casas_activas[casa],
                key=f"casa_{casa}"
            )

    st.success("Preferencias de casas guardadas")

# ---------------------------------
# LIGAS (GOOGLE SHEETS)
# ---------------------------------
elif menu == "🏆 Ligas":

    st.title("🏆 Ligas a Analizar")
    st.caption("🌍 Continente → 🏳️ País → ⚽ Ligas")

    try:
        df = pd.read_csv(LIGAS_CSV_URL)
    except Exception:
        st.error("❌ No se pudo cargar la base de datos desde Google Sheets")
        st.stop()

    # ---- NORMALIZAR COLUMNAS ----
    df.columns = (
        df.columns
        .str.upper()
        .str.strip()
    )

    columnas_requeridas = {"CONTINENTE", "PAIS", "LIGA", "ENCENDIDO"}
    if not columnas_requeridas.issubset(df.columns):
        st.error("❌ La hoja debe tener: CONTINENTE, PAIS, LIGA, ENCENDIDO")
        st.stop()

    if "ligas_activas" not in st.session_state:
        st.session_state.ligas_activas = {}

    # ---- ESTRUCTURA DESPLEGABLE ----
    for continente in sorted(df["CONTINENTE"].dropna().unique()):

        with st.expander(f"🌍 {continente}", expanded=False):

            df_cont = df[df["CONTINENTE"] == continente]

            for pais in sorted(df_cont["PAIS"].dropna().unique()):
                st.markdown(f"### 🏳️ {pais}")

                df_pais = df_cont[df_cont["PAIS"] == pais]

                for _, row in df_pais.iterrows():
                    liga = row["LIGA"]
                    encendido = str(row["ENCENDIDO"]).strip().upper() == "TRUE"

                    st.session_state.ligas_activas[liga] = st.checkbox(
                        liga,
                        value=st.session_state.ligas_activas.get(liga, encendido),
                        key=f"liga_{liga}"
                    )

    st.success("Ligas cargadas correctamente desde Google Sheets")

# ---------------------------------
# ANÁLISIS
# ---------------------------------
elif menu == "📊 Análisis":
    st.title("📊 Análisis")
    st.info("Módulo en construcción")

# ---------------------------------
# HERRAMIENTAS
# ---------------------------------
elif menu == "🧮 Herramientas":
    st.title("🧮 Herramientas")
    st.info("Módulo en construcción")

# ---------------------------------
# GESTIÓN
# ---------------------------------
elif menu == "💼 Gestión":
    st.title("💼 Gestión")
    st.info("Módulo en construcción")
