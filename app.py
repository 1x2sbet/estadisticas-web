import streamlit as st
import pandas as pd

st.set_page_config(page_title="Panel Estadístico", layout="wide")

st.title("📊 Plataforma de Análisis Estadístico")

st.subheader("Tabla de análisis (datos de prueba)")

df = pd.read_csv("data/datos_prueba.csv")

st.dataframe(df, use_container_width=True)

