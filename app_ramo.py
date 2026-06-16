import streamlit as st
import pandas as pd
from datetime import datetime

# INTENTAMOS IMPORTAR LAS LIBRERÍAS DE GOOGLE DE FORMA SEGURA
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Tool RAMO - Grup Sumarroca",
    page_icon="🍇",
    layout="wide"
)

# Estilos visuales corporativos
st.markdown('''
    <style>
    .main-title { font-size: 30px; font-weight: bold; color: #1e4620; margin-bottom: 5px; }
    .subtitle { font-size: 15px; color: #555555; margin-bottom: 25px; }
    .stButton>button { background-color: #1e4620; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    </style>
''', unsafe_allow_html=True)

st.markdown('<div class="main-title">🍇 Tool Interna Proyecto RAMO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grup Sumarroca — Registro Histórico de Acciones de Innovación y Sostenibilidad</div>', unsafe_allow_html=True)

# 2. CONEXIÓN A GOOGLE SHEETS (CON MODO CONTINGENCIA SEGURO)
@st.cache_resource
def init_connection():
    if not HAS_GOOGLE_LIBS:
        return None
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Intentamos validar con las claves guardadas en Secrets
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds)
    except Exception:
        return None

client = init_connection()
SHEET_NAME = "Registro_Proyecto_RAMO"

def load_data(client_obj):
    if client_obj is not None:
        try:
            sheet = client_obj.open(SHEET_NAME).sheet1
            return pd.DataFrame(sheet.get_all_records()), sheet
        except Exception:
            pass
    
    # Si falla Google, creamos un almacén local en la memoria para que la app NO se quede en blanco
    if 'local_df' not in st.session_state:
        st.session_state.local_df = pd.DataFrame(columns=[
            "Fecha", "Responsable", "Área/Bloque", "Tipo Impacto (ESG)", "Descripción de la Acción", "Repercusión / KPIs"
        ])
    return st.session_state.local_df, None

df, google_sheet = load_data(client)

# Si la conexión con Google falló, le avisamos al usuario amigablemente pero NO bloqueamos la pantalla
if google_sheet is None:
    st.warning("⚠️ Modo local temporal: Las credenciales de Google Sheets aún no se han validado correctamente o el archivo no se llama 'Registro_Proyecto_RAMO'. Los cambios se guardarán solo en esta sesión de navegador.")

# 3. INTERFAZ: PESTAÑAS (ESTO YA NO SE QUEDARÁ EN BLANCO)
tab1, tab2 = st.tabs(["📝 Registrar Nueva Acción", "📊 Histórico y Exportación"])

with tab1:
    st.subheader("Anotar Acción")
    with st.form("form_ramo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("1. Fecha de la Acción", datetime.now())
            responsable = st.text_input("2. Nombre del Responsable", placeholder="Ej. Marta Sumarroca")
            area = st.selectbox("3. Área / Bloque del Proyecto RAMO", [
                "Viticultura (Campo/Viñedo)",
                "Bodega (Elaboración/Crianza)",
                "Packaging (Botellas, Corchos, Etiquetas)",
                "Logística y Distribución",
                "Gestión del Agua y Vertidos",
                "Energía y Emisiones",
                "Enoturismo y Relaciones Sociales",
                "I+D / Ensayos de Innovación"
            ])
        with col2:
            esg_tipo = st.selectbox("4. Tipo de Impacto (Criterio ESG)", [
                "Ambiental (E - Environmental)",
                "Social (S - Social)",
                "Gobernanza e Innovación (G - Governance)"
            ])
            descripcion = st.text_area("5. Descripción Detallada", placeholder="Explica qué se ha hecho...")
            repercusion = st.text_area("6. Repercusión / KPIs Conseguidos", placeholder="Ej: Ahorro de agua...")
        
        submit_button = st.form_submit_button(label="Guardar Acción")
        
        if submit_button:
            if not responsable or not descripcion:
                st.error("Por favor, rellena el Responsable y la Descripción.")
            else:
                nueva_fila = [fecha.strftime("%Y-%m-%d"), responsable, area, esg_tipo, descripcion, repercusion]
                if google_sheet is not None:
                    try:
                        google_sheet.append_row(nueva_fila)
                        st.success("¡Acción guardada en la nube de Google Sheets!")
                    except Exception as e:
                        st.error(f"Error técnico al escribir: {e}")
               else:
                        df_new = pd.DataFrame([nueva_fila], columns=st.session_state.local_df.columns)
                        st.session_state.local_df = pd.concat([st.session_state.local_df, df_new], ignore_index=True)
                        st.success("¡Guardado localmente!")
                        st.rerun()

with tab2:
    st.subheader("Histórico de Acciones")
    st.dataframe(df, use_container_width=True)
