import streamlit as st

# ---------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------
st.set_page_config(
    page_title="1X2sBet",
    page_icon="⚽",
    layout="wide"
)

# ---------------------------------
# MENÚ LATERAL PRINCIPAL
# ---------------------------------
st.sidebar.title("⚽ 1X2sBet")

seccion = st.sidebar.radio(
    "Navegación",
    [
        "🏠 Inicio",
        "⚙️ Preferencias",
        "📊 Análisis",
        "🧮 Herramientas",
        "💼 Gestión"
    ],
    key="menu_principal"
)

# ---------------------------------
# CONTENIDO PRINCIPAL
# ---------------------------------

# ========= INICIO =========
if seccion == "🏠 Inicio":
    st.title("📊 Plataforma de Análisis Estadístico")
    st.write(
        """
        Bienvenido a **1X2sBet**.  
        Esta plataforma muestra análisis estadísticos generados automáticamente con Python.
        """
    )

# ========= PREFERENCIAS =========
elif seccion == "⚙️ Preferencias":

    submenu = st.selectbox(
        "Preferencias",
        ["Casas de Apuestas", "Ligas"],
        key="submenu_preferencias"
    )

    # ----- CASAS DE APUESTAS -----
    if submenu == "Casas de Apuestas":

        st.title("🏦 Casas de Apuestas Legales en Colombia")
        st.write("Activa o desactiva las casas que deseas usar en los análisis.")

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
            st.session_state.casas_activas = {casa: True for casa in casas}

        for casa, logo_path in casas.items():
            col1, col2 = st.columns([1, 6])

            with col1:
                st.image(logo_path, width=35)

            with col2:
                st.session_state.casas_activas[casa] = st.checkbox(
                    casa,
                    value=st.session_state.casas_activas[casa],
                    key=f"check_{casa}"
                )

        st.divider()
        st.success("Preferencias guardadas correctamente.")

    # ----- LIGAS -----
    import pandas as pd

elif submenu == "Ligas":

    st.title("🏆 Ligas a Analizar")
    st.write("Selecciona continentes, países y ligas desde la base de datos.")

    df = pd.read_csv("data/ligas.csv")

    # Filtro por continente
    continentes = sorted(df["continente"].unique())
    continente_sel = st.selectbox(
        "🌍 Continente",
        continentes,
        key="filtro_continente"
    )

    df_cont = df[df["continente"] == continente_sel]

    # Filtro por país
    paises = sorted(df_cont["pais"].unique())
    pais_sel = st.selectbox(
        "🏳️ País",
        paises,
        key="filtro_pais"
    )

    df_pais = df_cont[df_cont["pais"] == pais_sel]

    st.subheader("⚽ Ligas")

    if "ligas_activas" not in st.session_state:
        st.session_state.ligas_activas = {}

    for _, row in df_pais.iterrows():
        liga = row["liga"]
        valor_inicial = bool(row["activa"])

        st.session_state.ligas_activas[liga] = st.checkbox(
            liga,
            value=st.session_state.ligas_activas.get(liga, valor_inicial),
            key=f"liga_{liga}"
        )

    st.divider()
    st.success("Selección de ligas cargada desde la base de datos.")


# ========= ANÁLISIS =========
elif seccion == "📊 Análisis":

    submenu = st.selectbox(
        "Tipo de análisis",
        [
            "Análisis Ordenado",
            "Surebet",
            "Doble Oportunidad",
            "Apuestas de Valor"
        ],
        key="submenu_analisis"
    )

    st.title(f"📊 {submenu}")
    st.info("Módulo en construcción.")

# ========= HERRAMIENTAS =========
elif seccion == "🧮 Herramientas":

    submenu = st.selectbox(
        "Herramientas",
        ["Calculadora", "Convertidor de Bonos"],
        key="submenu_herramientas"
    )

    st.title(f"🧮 {submenu}")
    st.info("Herramienta en construcción.")

# ========= GESTIÓN =========
elif seccion == "💼 Gestión":

    submenu = st.selectbox(
        "Gestión",
        [
            "Control de Apuestas",
            "Historial de Transacciones",
            "Informe Anual"
        ],
        key="submenu_gestion"
    )

    st.title(f"💼 {submenu}")
    st.info("Sección en construcción.")
