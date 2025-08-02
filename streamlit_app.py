import streamlit as st
import firebase_admin
from firebase_admin import credentials
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

def format_value(value):
    if isinstance(value, str): return {"stringValue": value}
    if isinstance(value, int) or isinstance(value, float): return {"integerValue": str(value)}
    if isinstance(value, list):
        return {"arrayValue": {"values": [{"stringValue": str(v)} for v in value]}}
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
    url = f"https://firestore.googleapis.com/v1/{full_doc_path}"
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
            doc_data = {"seccion1_demograficos": {"pais": st.session_state.s1_pais, "departamento": st.session_state.s1_depto, "comunidad": st.session_state.s1_comunidad, "edad": st.session_state.s1_edad, "genero": st.session_state.s1_genero, "nivel_educativo": st.session_state.s1_educacion, "situacion_laboral": st.session_state.s1_laboral, "acceso_tecnologia": st.session_state.s1_tecnologia, "timestamp_inicio": datetime.datetime.now(datetime.timezone.utc).isoformat()}}
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

# --- SECCIONES 2, 3, 4 ---
# (Usan la lógica normal del formulario, pero ahora usan la función de update)

# --- SECCIÓN 2: PROBLEMÁTICAS LOCALES ---
elif st.session_state.current_section == 2:
    st.header("Sección 2: Problemáticas Locales")
    with st.form("form_s2"):
        st.text_area("1. Describe el problema principal que afecta a tu comunidad", placeholder='Ej: "Sequía en cultivos"', key="s2_problema")
        st.multiselect("2. ¿Con qué sectores se relaciona este problema?", ["Agricultura y tecnología", "Finanzas digitales", "Salud comunitaria", "Energía limpia"], key="s2_sectores")
        st.slider("3. Impacto del problema en tu comunidad (1=Bajo, 5=Crítico)", 1, 5, 3, key="s2_impacto")
        submitted_s2 = st.form_submit_button("Guardar y Continuar")
    if submitted_s2:
        if not st.session_state.s2_problema: st.warning("Por favor, describe el problema principal.")
        else:
            data_to_update = {"seccion2_problematicas": {"problema_principal": st.session_state.s2_problema, "sectores_relacionados": st.session_state.s2_sectores, "impacto_escala": st.session_state.s2_impacto}}
            success, error = update_data_rest(st.session_state.firestore_doc_path, data_to_update)
            if success:
                st.session_state.current_section = 3
                st.success("✅ ¡Sección 2 guardada! Avanzando...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Error al actualizar los datos."); st.exception(error)

# --- SECCIÓN 3: INTERESES PROFESIONALES ---
elif st.session_state.current_section == 3:
    st.header("Sección 3: Intereses Profesionales")
    with st.form("form_s3"):
        st.selectbox("1. ¿Cuál de estos sectores te atrae más?", ["", "AgriTech (Agricultura)", "FinTech (Finanzas)", "HealthTech (Salud)", "Energías Renovables"], key="s3_sector_interes")
        st.radio("2. ¿Cuál es tu nivel de experiencia en proyectos tecnológicos?", ["**UniExplorador** (Ninguna o baja experiencia)", "**UniCreador** (Experiencia básica)", "**UniVisionario** (Experiencia avanzada)"], key="s3_experiencia")
        submitted_s3 = st.form_submit_button("Guardar y Continuar")
    if submitted_s3:
        if not st.session_state.s3_sector_interes: st.warning("Por favor, selecciona un sector de interés.")
        else:
            nivel_autodeclarado = st.session_state.s3_experiencia.split("**")[1]
            data_to_update = {"seccion3_intereses": {"sector_interes_principal": st.session_state.s3_sector_interes, "nivel_autodeclarado": nivel_autodeclarado}}
            success, error = update_data_rest(st.session_state.firestore_doc_path, data_to_update)
            if success:
                st.session_state.current_section = 4
                st.success("✅ ¡Sección 3 guardada! Una más y terminamos.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Error al actualizar los datos."); st.exception(error)

# --- SECCIÓN 4: HABILIDADES TÉCNICAS Y BLANDAS ---
elif st.session_state.current_section == 4:
    st.header("Sección 4: Habilidades y Competencias")
    with st.form("form_s4"):
        st.subheader("Autoevaluación de Habilidades Técnicas")
        st.slider("1. En una escala de 1 (Nada) a 5 (Mucho), ¿qué tan cómodo te sientes con la programación o el análisis de datos?", 1, 5, 2, key="s4_autoeval_tech")
        st.subheader("Herramientas Conocidas")
        st.multiselect("2. Marca las herramientas o conceptos que conozcas", ["Sensores IoT", "Drones", "Plataformas de pago", "Blockchain", "Apps de Telemedicina", "Simulación de energía"], key="s4_herramientas")
        st.subheader("Habilidades Blandas")
        st.radio("3. Imagina que tu equipo discute sobre qué método usar en un proyecto. ¿Qué harías?", ["A) Dejo que otros decidan.", "B) Busco un consenso escuchando a todos.", "C) Analizo los datos y presento la solución más lógica."], key="s4_situacion_equipo")
        submitted_s4 = st.form_submit_button("Finalizar Diagnóstico")
    if submitted_s4:
        data_to_update = {"seccion4_habilidades": {"autoevaluacion_tech": st.session_state.s4_autoeval_tech, "herramientas_conocidas": st.session_state.s4_herramientas, "respuesta_habilidad_blanda": st.session_state.s4_situacion_equipo[0]}, "estado": "Completado", "timestamp_final": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        success, error = update_data_rest(st.session_state.firestore_doc_path, data_to_update)
        if success:
            st.session_state.current_section = 5
            st.success("✅ ¡Diagnóstico finalizado! Calculando tu perfil...")
            time.sleep(2)
            st.rerun()
        else:
            st.error("Error al actualizar los datos."); st.exception(error)

# --- SECCIÓN FINAL: RESULTADOS (EN CONSTRUCCIÓN) ---
elif st.session_state.current_section > 4:
    st.header("🎉 ¡Diagnóstico Completado! 🎉")
    st.balloons()
    st.markdown("¡Muchas gracias por completar tu diagnóstico! Hemos guardado tus respuestas de forma segura.")
    st.info(f"Tu ID de registro único es: **{st.session_state.firestore_doc_id}**")
    st.markdown("El siguiente paso será analizar tus respuestas para darte un resultado. ¡Estamos trabajando en ello!")
