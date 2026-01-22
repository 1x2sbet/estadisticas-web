import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Panel Estadístico",
    layout="wide"
)

# -------------------------------
# BARRA LATERAL (MENÚ)
# -------------------------------
st.sidebar.title("📊 1X2SBET")

opcion = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Tablas", "Análisis", "Configuración"]
)

# -------------------------------
# CONTENIDO PRINCIPAL
# -------------------------------
if opcion == "Inicio":
    st.title("📊 Plataforma de Análisis Estadístico")
    st.write("""
    Bienvenido a la plataforma.

    Aquí podrás consultar tablas y análisis estadísticos
    generados automáticamente desde distintas fuentes.
    """)

elif opcion == "Tablas":
    st.title("📋 Tablas estadísticas")

    df = pd.read_csv("data/datos_prueba.csv")
    st.dataframe(df, use_container_width=True)

elif opcion == "Análisis":
    st.title("📈 Análisis básico")

    df = pd.read_csv("data/datos_prueba.csv")

    st.bar_chart(
        df.set_index("Partido")[["Prob_Local", "Prob_Empate", "Prob_Visitante"]]
    )

elif opcion == "Configuración":
    st.title("⚙️ Configuración")
    st.write("Opciones de usuario y preferencias (próximamente)")


