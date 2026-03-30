import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_VALIDO = "admin"
CLAVE_VALIDA = "oks2026" 

def login():
    st.title("🔐 Acceso Privado OKS")
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if usuario == USUARIO_VALIDO and clave == CLAVE_VALIDA:
                st.session_state['logueado'] = True
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")

if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False

if not st.session_state['logueado']:
    login()
else:
    st.set_page_config(page_title="OKS - Visor Global", layout="wide")
    archivo_rutas = 'rutas_optimizadas.xlsx' 

    if os.path.exists(archivo_rutas):
        df = pd.read_excel(archivo_rutas)
        # Limpieza de nombres de columnas por seguridad
        df.columns = df.columns.str.strip()
        df['Codigo_Cliente'] = df['Codigo_Cliente'].astype(str).str.replace('.0', '', regex=False).str.strip()
        
        st.title("🗺️ Panel de Supervisión OKS - Perfil Comercial")
        
        st.sidebar.header("Filtros de Búsqueda")
        vendedores_sel = st.sidebar.multiselect("Seleccionar Vendedores:", sorted(df['Vendedor'].unique().tolist()))
        dias_sel = st.sidebar.multiselect("Seleccionar Días:", ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado'], default=[])

        if vendedores_sel and dias_sel:
            df_f = df[(df['Vendedor'].isin(vendedores_sel)) & (df['Dia'].isin(dias_sel))]
            
            if not df_f.empty:
                centro = [df_f['Latitud'].mean(), df_f['Longitud'].mean()]
                m = folium.Map(location=centro, zoom_start=12, tiles='cartodbpositron')

                for _, row in df_f.iterrows():
                    coord = [row['Latitud'], row['Longitud']]
                    
                    # --- LÓGICA DE COLORES POR DÍA Y COMPRA ---
                    promedio = row.get('Promedio_3Meses', 'NA')
                    
                    # Determinamos si tiene compra (si no es NA, N/A o nulo)
                    tiene_compra = True
                    if pd.isna(promedio) or str(promedio).strip().upper() in ['NA', 'N/A', '', 'NAN']:
                        tiene_compra = False

                    # Asignación de colores según la librería de Folium
                    if row['Dia'] == 'Lunes':
                        color_pin = 'darkred' if tiene_compra else 'red'
                    elif row['Dia'] == 'Martes':
                        color_pin = 'darkblue' if tiene_compra else 'lightblue'
                    elif row['Dia'] == 'Miercoles':
                        color_pin = 'darkgreen' if tiene_compra else 'lightgreen'
                    elif row['Dia'] == 'Jueves':
                        # --- MODIFICACIÓN SOLICITADA PARA EL JUEVES ---
                        color_pin = 'brown' if tiene_compra else 'orange' 
                        # ---------------------------------------------
                    elif row['Dia'] == 'Viernes':
                        color_pin = 'darkpurple' if tiene_compra else 'purple' # 'purple' actúa como lila
                    else:
                        color_pin = 'black' # Fallback para Sábado/Domingo
                    
                    # Validación para no mostrar "NA" en el Vendedor Anterior
                    vend_ant = row.get('Vendedor_Anterior', '')
                    if pd.isna(vend_ant) or str(vend_ant).strip().upper() in ['NA', 'N/A', 'NAN']:
                        vend_ant = '' 
                        
                    # --- POPUP MEJORADO CON TODA LA INFO COMERCIAL ---
                    html_popup = f"""
                    <div style="font-family: Arial, sans-serif; min-width: 250px; font-size: 12px;">
                        <h4 style="margin: 0 0 5px 0; color: #d32f2f;">{row['Cliente']}</h4>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td><b>Código:</b></td><td>{row['Codigo_Cliente']}</td></tr>
                            <tr><td><b>Vendedor:</b></td><td>{row['Vendedor']}</td></tr>
                            <tr><td><b>Supervisor:</b></td><td>{row.get('Supervisor', 'N/A')}</td></tr>
                            <tr><td><b>Día:</b></td><td>{row['Dia']}</td></tr>
                            
                            <tr><td colspan="2"><hr style="margin: 5px 0; border: 0; border-top: 1px solid #ccc;"></td></tr>
                            
                            <tr><td><b>Canal:</b></td><td>{row.get('Canal', 'N/A')}</td></tr>
                            <tr><td><b>Frec. Trim:</b></td><td>{row.get('Frecuencia_Trismestral', 'N/A')}</td></tr>
                            <tr><td><b>PDV Compra:</b></td><td>{row.get('PDV_COMPRA', 'N/A')}</td></tr>
                            <tr><td><b>Prom. 3 Meses:</b></td><td>{row.get('Promedio_3Meses', 'N/A')}</td></tr>
                            <tr><td><b>Pago:</b></td><td>{row.get('Forma_de_Pago', 'N/A')}</td></tr>
                            <tr><td><b>Vend. Ant:</b></td><td>{vend_ant}</td></tr>
                            
                            <tr><td colspan="2"><hr style="margin: 5px 0; border: 0; border-top: 1px solid #ccc;"></td></tr>
                            
                            <tr><td colspan="2"><b>Dirección:</b><br>{row['Direccion_Completa']}</td></tr>
                        </table>
                    </div>
                    """
                    
                    folium.Marker(
                        location=coord,
                        popup=folium.Popup(html_popup, max_width=350), 
                        tooltip=f"Perfil: {row['Cliente']}",
                        icon=folium.Icon(color=color_pin, icon='info-sign')
                    ).add_to(m)

                    folium.Marker(
                        location=coord,
                        icon=folium.DivIcon(
                            icon_size=(150,36),
                            icon_anchor=(7, 18),
                            html=f"""<div style="font-family: 'Arial Black'; color: #000; font-size: 10pt; font-weight: 900; text-shadow: 1px 1px 0 #FFF, -1px -1px 0 #FFF, 1px -1px 0 #FFF, -1px 1px 0 #FFF;">{row['Codigo_Cliente']}</div>"""
                        )
                    ).add_to(m)
                
                st_folium(m, width=1400, height=750, returned_objects=[])
            else:
                st.warning("No se encontraron registros.")
        else:
            st.info("👈 Selecciona Vendedor y Día en el menú lateral.")
            
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['logueado'] = False
            st.rerun()
    else:
        st.error("Archivo 'rutas_optimizadas.xlsx' no encontrado.")
