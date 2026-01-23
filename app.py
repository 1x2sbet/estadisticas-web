import streamlit as st
import pandas as pd
import os

# ---------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------
st.set_page_config(
    page_title="1X2sBet",
    page_icon="⚽",
    layout="wide"
)

# ---------------------------------
# MENÚ LATERAL
# ---------------------------------
st.sidebar.title("⚽ 1X2sBet")

seccion = st.sidebar.radio(
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
if seccion == "🏠 Inicio":
    st.title("📊 Plataforma de Análisis Estadístico")
    st.write("Bienvenido a **1X2sBet**.")

# ---------------------------------
# CASAS DE APUESTAS
# ---------------------------------
elif seccion == "🏦 Casas de Apuestas":

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

# ---------------------------------
# LIGAS DESPLEGABLES
# ---------------------------------
elif seccion == "🏆 Ligas":

    st.title("🏆 Ligas a Analizar")
    st.write("Despliega por continente y país para activar ligas.")

    ruta_csv = "data/data/ligas.csv"

    if not os.path.exists(ruta_csv):
        st.error("❌ No se encontró el archivo data/data/ligas.csv")
        st.stop()

    df = pd.read_csv(ruta_csv)

    # LIMPIEZA CRÍTICA (ESTO SOLUCIONA EL ERROR)
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=["continente", "pais", "liga"])
    df["continente"] = df["continente"].astype(str)
    df["pais"] = df["pais"].astype(str)
    df["liga"] = df["liga"].astype(str)

    if "ligas_activas" not in st.session_state:
        st.session_state.ligas_activas = {}

    # CONTINENTES
    for continente in sorted(df["continente"].unique().tolist()):
        with st.expander(f"🌍 {continente}", expanded=False):

            df_cont = df[df["continente"] == continente]

            # PAÍSES
            for pais in sorted(df_cont["pais"].unique().tolist()):
                with st.expander(f"🏳️ {pais}", expanded=False):

                    df_pais = df_cont[df_cont["pais"] == pais]

                    # LIGAS
                    for _, row in df_pais.iterrows():
                        liga = row["liga"]
                        activa = bool(row.get("activa", True))

                        st.session_state.ligas_activas[liga] = st.checkbox(
                            liga,
                            value=st.session_state.ligas_activas.get(liga, activa),
                            key=f"liga_{continente}_{pais}_{liga}"
                        )

    st.success("✅ Ligas cargadas correctamente.")

# ---------------------------------
# OTROS MÓDULOS
# ---------------------------------
elif seccion == "📊 Análisis":
    st.title("📊 Análisis")
    st.info("En construcción")

elif seccion == "🧮 Herramientas":
    st.title("🧮 Herramientas")
    st.info("En construcción")

elif seccion == "💼 Gestión":
    st.title("💼 Gestión")
    st.info("En construcción")
