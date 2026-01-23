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
# CONTENIDO
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
            "BETANO": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Betano_logo.png",
            "BETPLAY": "https://upload.wikimedia.org/wikipedia/commons/5/5f/BetPlay_logo.png",
            "BETSSON": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Betsson_logo.png",
            "BINGOCASINOS": "https://bingocasinos.com.co/favicon.ico",
            "BWIN": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Bwin_logo.svg",
            "CODERE": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Codere_logo.png",
            "LUCKIA": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Luckia_logo.png",
            "RIVALO": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Rivalo_logo.png",
            "RUSHBET": "https://upload.wikimedia.org/wikipedia/commons/0/08/Rushbet_logo.png",
            "SPORTIUM": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Sportium_logo.png",
            "STAKE": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Stake_logo.png",
            "WPLAY": "https://upload.wikimedia.org/wikipedia/commons/8/8b/Wplay_logo.png",
            "YAJUEGO": "https://yajuego.com.co/favicon.ico",
            "ZAMBA": "https://zamba.co/favicon.ico",
        }

        if "casas_activas" not in st.session_state:
            st.session_state.casas_activas = {casa: True for casa in casas}

        for casa, logo in casas.items():
            col1, col2 = st.columns([1, 6])

            with col1:
                st.image(logo, width=30)

            with col2:
                st.session_state.casas_activas[casa] = st.checkbox(
                    casa,
                    value=st.session_state.casas_activas[casa],
                    key=f"check_{casa}"
                )

        st.divider()
        st.success("Preferencias guardadas para esta sesión.")

    # ----- LIGAS -----
    elif submenu == "Ligas":
        st.title("🏆 Ligas")
        st.info("Este módulo se construirá después.")

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
