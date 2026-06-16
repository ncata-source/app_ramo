import streamlit as st
import pandas as pd
from datetime import datetime

# Intentamos importar las librerías de Google Sheets de forma segura
try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    pass

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Tool RAMO - Grup Sumarroca",
    page_icon="🍇",
    layout="wide"
)

# Estilos visuales personalizados con los colores corporativos (Verde Sumarroca, gris y blanco)
st.markdown('''
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #1e4620;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 16px;
        color: #555555;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #1e4620;
        color: white;
        border-radius: 5px;
        width: 100%;
    }
    </style>
''', unsafe_allow_html=True)

st.markdown('<div class="main-title">🍇 Tool Interna Proyecto RAMO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grup Sumarroca — Registro Histórico de Acciones de Innovación y Sostenibilidad</div>', unsafe_allow_html=True)

# 2. CONEXIÓN EN TIEMPO REAL A GOOGLE SHEETS
@st.cache_resource
def init_connection():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        # Conexión usando los secretos seguros de Streamlit Cloud
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

try:
    client = init_connection()
except:
    client = None

# Nombre del archivo Excel en tu Google Drive
SHEET_NAME = "Registro_Proyecto_RAMO"

def load_data(client):
    if client is not None:
        try:
            sheet = client.open(SHEET_NAME).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data), sheet
        except Exception as e:
            st.warning("Conectado al motor, pero no se encontró la hoja 'Registro_Proyecto_RAMO' o las columnas no coinciden.")
    
    # Almacenamiento temporal si falla la conexión en la nube temporalmente
    if 'local_df' not in st.session_state:
        st.session_state.local_df = pd.DataFrame(columns=[
            "Fecha", "Responsable", "Área/Bloque", "Tipo Impacto (ESG)", "Descripción de la Acción", "Repercusión / KPIs"
        ])
    return st.session_state.local_df, None

df, google_sheet = load_data(client)

# 3. DISEÑO DE PESTAÑAS (FORMULARIO E HISTÓRICO)
tab1, tab2 = st.tabs(["📝 Registrar Nueva Acción", "📊 Histórico y Exportación"])

# PESTAÑA 1: FORMULARIO DE
