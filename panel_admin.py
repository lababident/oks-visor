import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Cambia 'admin123' por la clave que tú quieras
USUARIO_VALIDO = "admin"
CLAVE_VALIDA = "oks2026" 

def login():
    st.title("🔐 Acceso Privado OKS")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_VALIDO and clave == CLAVE_VALIDA:
            st.session_state['logueado'] = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")

# Inicializar estado de login
if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False

if not st.session_state['logueado']:
    login()
else:
    # --- AQUÍ EMPIEZA TU PANEL DE SIEMPRE ---
    st.set_page_config(page_title="OKS - Visor Global", layout="wide")
    
    # IMPORTANTE: En la nube el archivo debe estar en la misma carpeta
    archivo_rutas = 'rutas_optimizadas.xlsx' 

    COLORES_DIAS = {
        'Lunes': 'red', 'Martes': 'blue', 'Miercoles': 'green',
        'Jueves': 'orange', 'Viernes': 'purple', 'Sabado': 'black', 'Domingo': 'gray'
    }

    if os.path.exists(archivo_rutas):
        df = pd.read_excel(archivo_rutas)
        df['Codigo_Cliente'] = df['Codigo_Cliente'].astype(str).str.replace('.0', '', regex=False)
        
        st.title("🗺️ Panel de Supervisión OKS")
        
        st.sidebar.header("Filtros")
        vendedores_sel = st.sidebar.multiselect("Vendedores:", sorted(df['Vendedor'].unique().tolist()))
        dias_sel = st.sidebar.multiselect("Días:", ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes'], default=[])

        if vendedores_sel and dias_sel:
            df_f = df[(df['Vendedor'].isin(vendedores_sel)) & (df['Dia'].isin(dias_sel))]
            if not df_f.empty:
                centro = [df_f['Latitud'].mean(), df_f['Longitud'].mean()]
                m = folium.Map(location=centro, zoom_start=12, tiles='cartodbpositron')

                for _, row in df_f.iterrows():
                    coord = [row['Latitud'], row['Longitud']]
                    color = COLORES_DIAS.get(row['Dia'], 'blue')
                    folium.Marker(location=coord, icon=folium.Icon(color=color, icon='info-sign')).add_to(m)
                    folium.Marker(location=coord, icon=folium.DivIcon(icon_size=(150,36), icon_anchor=(7, 18),
                        html=f"""<div style="font-family: 'Arial Black'; color: #000; font-size: 10pt; font-weight: 900; text-shadow: 1px 1px 0 #FFF, -1px -1px 0 #FFF;">{row['Codigo_Cliente']}</div>""")).add_to(m)
                
                st_folium(m, width=1400, height=700)
            else:
                st.warning("No hay datos para esta selección.")
        else:
            st.info("👈 Selecciona filtros en el menú lateral.")
            
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['logueado'] = False
            st.rerun()
    else:
        st.error("Archivo 'rutas_optimizadas.xlsx' no encontrado en el servidor.")
