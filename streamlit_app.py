import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import datetime

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
PROJECT_ID = "diagnostico-unidigihub"
creds_dict = None

def get_credentials():
    global creds_dict
    if creds_dict: return creds_dict
    try:
        creds_from_secrets = st.secrets["firebase_credentials"]
        creds_dict = dict(creds_from_secrets) if not isinstance(creds_from_secrets, str) else json.loads(creds_from_secrets)
        return creds_dict
    except Exception as e:
        st.error(f"Error CRÍTICO al leer las credenciales: {e}")
        st.stop()

def get_access_token():
    try:
        creds_info = get_credentials()
        scopes = ['https://www.googleapis.com/auth/datastore']
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)
        if not creds.token:
            creds.refresh(Request())
        return creds.token
    except Exception as e:
        st.error("No se pudo obtener el token de acceso para Firestore.")
        st.exception(e)
        return None

# --- FUNCIÓN DE FORMATO CORREGIDA ---
def format_value(value):
    if isinstance(value, str):
        # Manejo especial para Timestamps en formato ISO
        try:
            datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
            return {"timestampValue": value}
        except ValueError:
            return {"stringValue": value}
    if isinstance(value, int) or isinstance(value, float): return {"integerValue": str(value)}
    if isinstance(value, list):
        if not value: return {"arrayValue": {}}
        else: return {"arrayValue": {"values": [{"stringValue": str(v)} for v in value]}}
    # NUEVA LÓGICA: Enseña al programa a manejar "sobres" (diccionarios anidados)
    if isinstance(value, dict):
        return {"mapValue": {"fields": {k: format_value(v) for k, v in value.items()}}}
    return {}

def save_data_rest(collection, data):
    access_token = get_access_token()
    if not access_token: return False, None, "Fallo en obtener token"
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    firestore_data = {"fields": {key: format_value(value) for key, value in data.items()}}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(firestore_data))
        response.raise_for_status()
        doc_name = response.json().get("name", "").split("/")[-1]
        return True, doc_name, None
    except Exception as e:
        return False, None, e

def update_data_rest(full_doc_path, data_to_update):
    access_token = get_access_token()
    if not access_token: return False, "Fallo en obtener token"
    # Construimos la URL de actualización con los campos a modificar
    update_mask = '&'.join([f'updateMask.fieldPaths={key}' for key in data_to_update.keys()])
    url = f"https://firestore.googleapis.com/v1/{full_doc_path}?{update_mask}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    firestore_data = {"fields": {key: format_value(value) for key, value in data_to_update.items()}}

    try:
        response = requests.patch(url, headers=headers, data=json.dumps(firestore_data))
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, e

# --- CONFIGURACIÓN DE PÁGINA Y ESTADO ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")
if "current_section" not in st.session_state: st.session_state.current_section = 1
if "firestore_doc_id" not in st.session_state: st.session_state.firestore_doc_id = None
if "firestore_doc_path" not in st.session_state: st.session_state.firestore_doc_path = None

st.title("📝 Diagnóstico UniDigiHub LATAM")
total_sections = 7
progress_text = f"Progreso: Sección {st.session_state.current_section} de {total_sections}"
st.progress(st.session_state.current_section / total_sections, text=progress_text)
st.markdown("---")

# --- SECCIÓN 1: DATOS DEMOGRÁFICOS ---
if st.session_state.current_section == 1:
    st.header("Sección 1: Datos Demográficos")
    st.markdown("""
    ### 👋 ¡Bienvenida y bienvenido! 
    Este autodiagnóstico tiene como propósito conocerte mejor para ayudarte a identificar tu punto de partida en el mundo digital. A través de 7 secciones breves, exploraremos tus intereses, habilidades y contexto local para recomendarte una ruta de aprendizaje personalizada dentro de UniDigiHub.
    💡 **Tu participación nos permitirá diseñar experiencias formativas más inclusivas, útiles y adaptadas a tu realidad.**
    No se requiere experiencia previa. Solo responde con sinceridad 😊
    """)
    with st.form("form_s1"):
        st.selectbox("1. ¿En qué país resides?", ["", "México (Mēxihco)", "Colombia", "Chile", "Brasil", "Argentina", "Costa Rica", "Ecuador", "El Salvador", "Perú"], key="s1_pais")
        st.text_input("2. Departamento o Estado donde vives", key="s1_depto")
        st.text_input("3. Municipio o comunidad", key="s1_comunidad")
        st.slider("4. ¿Cuál es tu edad?", min_value=25, max_value=90, value=25, step=1, key="s1_edad")
        st.selectbox("5. ¿Con qué género te identificas?", ["", "Femenino", "Masculino", "No binario", "Prefiero no decir", "Muxe (zapoteco)", "Otro"], key="s1_genero")
        st.selectbox("6. ¿Cuál es tu nivel educativo más alto alcanzado?", ["", "Primaria incompleta", "Primaria completa", "Secundaria", "Técnico", "Universitario 🎓", "Posgrado"], key="s1_educacion")
        st.multiselect("7. ¿Cuál es tu situación laboral actual?", ["Agricultura de subsistencia", "Empleo informal", "Estudiante", "Desempleado", "Trabajo remoto"], key="s1_laboral")
        st.multiselect("8. ¿Qué acceso tecnológico tienes actualmente?", ["📱 Teléfono móvil (sin internet)", "📱💻 Teléfono con internet", "💻 Computadora/Tablet", "📶 Internet estable en casa", "❌ Ninguno"], key="s1_tecnologia")
        submitted_s1 = st.form_submit_button("Guardar y Continuar")

    if submitted_s1:
        campos_obligatorios = {"País": st.session_state.s1_pais, "Departamento o Estado": st.session_state.s1_depto, "Municipio o comunidad": st.session_state.s1_comunidad, "Género": st.session_state.s1_genero, "Nivel educativo": st.session_state.s1_educacion}
        campos_faltantes = [nombre for nombre, valor in campos_obligatorios.items() if not valor]
        if campos_faltantes:
            st.error(f"🚨 ¡Atención! Por favor, completa los siguientes campos: **{', '.join(campos_faltantes)}**.")
        else:
            doc_data = {"seccion1_demograficos": {"pais": st.session_state.s1_pais, "departamento": st.session_state.s1_depto, "comunidad": st.session_state.s1_comunidad, "edad": st.session_state.s1_edad, "genero": st.session_state.s1_genero, "nivel_educativo": st.session_state.s1_educacion, "situacion_laboral": st.session_state.s1_laboral, "acceso_tecnologia": st.session_state.s1_tecnologia}, "timestamp_inicio": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            success, doc_id, error = save_data_rest("respuestas_diagnostico_unificado", doc_data)
            if success:
                st.session_state.firestore_doc_id = doc_id
                st.session_state.firestore_doc_path = f"projects/{PROJECT_ID}/databases/(default)/documents/respuestas_diagnostico_unificado/{doc_id}"
                st.session_state.current_section = 2
                st.success("✅ ¡Sección 1 guardada! Avanzando...")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Houston, tenemos un problema al guardar los datos.")
                st.exception(error)

# --- SECCIONES RESTANTES ---
elif st.session_state.current_section == 2:
    st.header("Sección 2: Problemáticas Locales")
    # ... (El código para las demás secciones irá aquí en el futuro)
    st.info("La Sección 1 funciona. ¡Ahora podemos construir el resto del formulario!")
    
# ... y así sucesivamente para las demás secciones ...
