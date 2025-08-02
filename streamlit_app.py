import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import datetime # <--- LA CORRECCIÓN ESTÁ AQUÍ

# --- INICIALIZACIÓN Y FUNCIONES PARA GUARDAR DATOS ---
PROJECT_ID = "diagnostico-unidigihub"
creds_dict = None

# Esta función obtiene las credenciales de los secrets
def get_credentials():
    global creds_dict
    if creds_dict:
        return creds_dict
    try:
        creds_from_secrets = st.secrets["firebase_credentials"]
        if isinstance(creds_from_secrets, str):
            creds_dict = json.loads(creds_from_secrets)
        else:
            creds_dict = dict(creds_from_secrets)
        return creds_dict
    except Exception as e:
        st.error(f"Error CRÍTICO: No se pudieron leer las credenciales desde los 'Secrets'. Error: {e}")
        st.stop()

# Nueva función para guardar datos usando el método de "Correo Postal" (REST API)
def save_data_rest(collection_name, data):
    try:
        creds_info = get_credentials()
        creds = service_account.Credentials.from_service_account_info(creds_info)
        
        if not creds.token:
            creds.refresh(Request())
        
        access_token = creds.token
        
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection_name}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Convertir datos al formato que Firestore REST API espera
        firestore_data = {"fields": {}}
        for key, value in data.items():
            if isinstance(value, str):
                firestore_data["fields"][key] = {"stringValue": value}
            elif isinstance(value, int) or isinstance(value, float):
                firestore_data["fields"][key] = {"integerValue": str(value)}
            elif isinstance(value, list):
                 firestore_data["fields"][key] = {"arrayValue": {"values": [{"stringValue": str(v)} for v in value]}}
            # Se pueden añadir más tipos si es necesario
        
        response = requests.post(url, headers=headers, data=json.dumps(firestore_data))
        response.raise_for_status() # Lanza un error si la respuesta no es 2xx
        
        # Extraer el ID del nuevo documento de la respuesta
        response_json = response.json()
        doc_name = response_json.get("name", "").split("/")[-1]
        return True, doc_name, None

    except Exception as e:
        return False, None, e

# --- CONFIGURACIÓN DE PÁGINA Y ESTADO DE SESIÓN ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")

if "current_section" not in st.session_state:
    st.session_state.current_section = 1
if "firestore_doc_id" not in st.session_state:
    st.session_state.firestore_doc_id = None

# --- TÍTULO Y BARRA DE PROGRESO ---
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
        campos_obligatorios = {
            "País": st.session_state.s1_pais, "Departamento o Estado": st.session_state.s1_depto,
            "Municipio o comunidad": st.session_state.s1_comunidad, "Género": st.session_state.s1_genero,
            "Nivel educativo": st.session_state.s1_educacion
        }
        campos_faltantes = [nombre for nombre, valor in campos_obligatorios.items() if not valor]
        if campos_faltantes:
            st.error(f"🚨 ¡Atención! Por favor, completa los siguientes campos: **{', '.join(campos_faltantes)}**.")
        else:
            doc_data = {
                "pais": st.session_state.s1_pais, "departamento": st.session_state.s1_depto,
                "comunidad": st.session_state.s1_comunidad, "edad": st.session_state.s1_edad,
                "genero": st.session_state.s1_genero, "nivel_educativo": st.session_state.s1_educacion,
                "situacion_laboral": st.session_state.s1_laboral, "acceso_tecnologia": st.session_state.s1_tecnologia,
                "timestamp_inicio": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            success, doc_id, error = save_data_rest("respuestas_diagnostico_unificado", doc_data)
            if success:
                st.session_state.firestore_doc_id = doc_id
                st.session_state.current_section = 2
                st.success("✅ ¡Sección 1 guardada con el nuevo método! Avanzando...")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Houston, tenemos un problema final al guardar los datos.")
                st.exception(error)

# --- (El resto de las secciones usarán la librería normal de Firebase para actualizar, lo cual es más sencillo) ---
elif st.session_state.current_section > 1:
    st.header("🎉 ¡Éxito! 🎉")
    st.balloons()
    st.success("La primera sección se guardó correctamente. El problema principal está resuelto.")
    st.info(f"Tu ID de registro es: {st.session_state.firestore_doc_id}")
    st.markdown("Ahora podemos continuar construyendo el resto de las secciones.")
