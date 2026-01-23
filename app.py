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

