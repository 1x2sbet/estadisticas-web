import streamlit as st
# -------------------------------
# MENÚ LATERAL
# -------------------------------
st.sidebar.title("⚽ 1X2sBet")

seccion = st.sidebar.radio(
    "Navegación",
    [
        "🏠 Inicio",
        "⚙️ Preferencias",
        "📊 Análisis",
        "🧮 Herramientas",
        "💼 Gestión"
    ]
)

# -------------------------------
# CONTENIDO PRINCIPAL
# -------------------------------

if seccion == "🏠 Inicio":
    st.title("⚽ 1X2sBet")
    st.write("Plataforma de Análisis de apuestas de futból. Está diseñado sólo para las casas de puestas legales en Colombia.")

# -------- PREFERENCIAS --------
elif seccion == "⚙️ Preferencias":
    submenu = st.selectbox(
        "Preferencias",
        ["Casas de Apuestas", "Ligas"]
    )

    # ---------------- CASAS DE APUESTAS ----------------
    if submenu == "Casas de Apuestas":
        st.title("🏦 Casas de Apuestas Legales en Colombia")
        st.write("Activa o desactiva las casas de apuestas que deseas usar en los análisis.")

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
            st.session_state.casas_activas = {}

        for casa, logo in casas.items():
            col1, col2 = st.columns([1, 6])

            with col1:
                st.image(logo, width=30)

            with col2:
                activo = st.checkbox(
                    casa,
                    value=st.session_state.casas_activas.get(casa, True),
                    key=casa
                )
                st.session_state.casas_activas[casa] = activo

        st.divider()
        st.success("Preferencias guardadas para esta sesión.")

    # ---------------- LIGAS ----------------
    elif submenu == "Ligas":
        st.title("🏆 Ligas")
        st.info("Configuración de ligas (lo haremos después).")

    submenu = st.selectbox(
        "Preferencias",
        ["Casas de Apuestas", "Ligas"]
    )

    if submenu == "Casas de Apuestas":
        st.title("🏦 Casas de Apuestas")
        st.info("Configuración y selección de casas de apuestas.")

    elif submenu == "Ligas":
        st.title("🏆 Ligas")
        st.info("Selección de ligas a analizar.")

# -------- ANÁLISIS --------
elif seccion == "📊 Análisis":
    submenu = st.selectbox(
        "Tipo de análisis",
        [
            "Análisis Ordenado",
            "Surebet",
            "Doble Oportunidad",
            "Apuestas de Valor"
        ]
    )

    st.title(f"📊 {submenu}")
    st.info(f"Módulo de {submenu.lower()} (en construcción).")

# -------- HERRAMIENTAS --------
elif seccion == "🧮 Herramientas":
    submenu = st.selectbox(
        "Herramientas",
        ["Calculadora", "Convertidor de Bonos"]
    )

    st.title(f"🧮 {submenu}")
    st.info(f"Herramienta: {submenu.lower()}.")

# -------- GESTIÓN --------
elif seccion == "💼 Gestión":
    submenu = st.selectbox(
        "Gestión",
        [
            "Control de Apuestas",
            "Historial de Transacciones",
            "Informe Anual"
        ]
    )

    st.title(f"💼 {submenu}")
    st.info(f"Sección de {submenu.lower()}.")

