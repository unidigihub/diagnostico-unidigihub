import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time
import datetime

# --- INICIALIZACIÓN DE FIREBASE (NO TOCAR) ---
def initialize_firebase():
    try:
        creds_from_secrets = st.secrets["firebase_credentials"]
        if isinstance(creds_from_secrets, str):
            creds_dict = json.loads(creds_from_secrets)
        else:
            creds_dict = dict(creds_from_secrets)
        
        cred = credentials.Certificate(creds_dict)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return True, None
    except Exception as e:
        return False, e

IS_FIREBASE_INITIALIZED, FIREBASE_ERROR = initialize_firebase()
db = firestore.client() if IS_FIREBASE_INITIALIZED else None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")

# --- NAVEGACIÓN ---
st.sidebar.title("Navegación")
page = st.sidebar.radio("Elige una sección:", ["Formulario de Diagnóstico", "Prueba de Conexión"])

# --- PÁGINA 1: FORMULARIO ---
if page == "Formulario de Diagnóstico":
    if "current_section" not in st.session_state:
        st.session_state.current_section = 1
    if "firestore_doc_id" not in st.session_state:
        st.session_state.firestore_doc_id = None

    st.title("📝 Diagnóstico UniDigiHub LATAM")
    total_sections = 5
    progress_text = f"Progreso: Sección {st.session_state.current_section} de {total_sections}"
    st.progress(st.session_state.current_section / total_sections, text=progress_text)
    st.markdown("---")

    if st.session_state.current_section == 1:
        st.header("Sección 1: Datos Demográficos")
        with st.form("form_s1"):
            paises = ["", "México (Mēxihco)", "Colombia", "Chile", "Brasil", "Argentina", "Costa Rica", "Ecuador", "El Salvador", "Perú"]
            st.selectbox("1. ¿En qué país resides?", paises, key="s1_pais")
            st.text_input("2. Departamento o Estado donde vives", key="s1_depto")
            st.text_input("3. Municipio o comunidad", key="s1_comunidad")
            st.slider("4. ¿Cuál es tu edad?", min_value=15, max_value=90, value=25, step=1, key="s1_edad")
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
                st.error(f"🚨 ¡Atención! Por favor, completa los siguientes campos para continuar: **{', '.join(campos_faltantes)}**.")
            else:
                try:
                    doc_data = {"seccion1_demograficos": {"pais": st.session_state.s1_pais, "departamento": st.session_state.s1_depto, "comunidad": st.session_state.s1_comunidad, "edad": st.session_state.s1_edad, "genero": st.session_state.s1_genero, "nivel_educativo": st.session_state.s1_educacion, "situacion_laboral": st.session_state.s1_laboral, "acceso_tecnologia": st.session_state.s1_tecnologia,}, "timestamp_inicio": firestore.SERVER_TIMESTAMP}
                    _, doc_ref = db.collection("respuestas_diagnostico_unificado").add(doc_data)
                    st.session_state.firestore_doc_id = doc_ref.id
                    st.session_state.current_section = 2
                    st.success("✅ ¡Sección 1 guardada! Avanzando...")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error("Houston, tenemos un problema al guardar los datos.")
                    st.exception(e)
    # ... (El resto de las secciones del formulario van aquí, no se modifican) ...

# --- PÁGINA 2: PRUEBA DE CONEXIÓN ---
elif page == "Prueba de Conexión":
    st.header("Herramienta de Diagnóstico de Conexión 👨‍🔧")
    st.write("Esta herramienta verificará cada paso de la conexión a Firebase para encontrar el problema.")

    if st.button("Realizar Prueba de Conexión a Firebase"):
        with st.spinner("Realizando pruebas..."):
            # PRUEBA 1: Chequear si los secrets existen
            st.subheader("Prueba 1: Lectura de 'Secrets'")
            try:
                creds_from_secrets = st.secrets["firebase_credentials"]
                st.success("✅ ÉXITO: Las credenciales se leyeron correctamente desde los 'Secrets' de Streamlit.")
            except Exception as e:
                st.error("❌ FALLO: No se pudieron leer las credenciales desde los 'Secrets'.")
                st.error("SOLUCIÓN: Asegúrate de haber copiado y pegado correctamente las credenciales en la sección 'Settings -> Secrets' de tu app en Streamlit Cloud.")
                st.stop()

            # PRUEBA 2: Chequear inicialización de Firebase
            st.subheader("Prueba 2: Inicialización de la App de Firebase")
            if IS_FIREBASE_INITIALIZED:
                st.success("✅ ÉXITO: La aplicación de Firebase se inicializó correctamente con las credenciales.")
            else:
                st.error("❌ FALLO: La aplicación de Firebase no se pudo inicializar.")
                st.error(f"Detalle del error: {FIREBASE_ERROR}")
                st.stop()
            
            # PRUEBA 3: Escritura en Firestore
            st.subheader("Prueba 3: Escritura en la Base de Datos")
            try:
                test_collection = db.collection("test_diagnostico")
                test_doc_name = f"test_{int(time.time())}"
                test_collection.document(test_doc_name).set({
                    "mensaje": "Prueba de escritura exitosa",
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                st.success("✅ ÉXITO: Se escribió un documento de prueba en la base de datos.")
                st.info(f"Se creó un documento llamado '{test_doc_name}' en la colección 'test_diagnostico'.")
            except Exception as e:
                st.error("❌ FALLO: Se produjo un error al intentar escribir en la base de datos de Firestore.")
                st.error("Este es el error más común. Posibles soluciones:")
                st.error("1. **API Deshabilitada:** Asegúrate de que la API 'Cloud Firestore API' esté HABILITADA en tu proyecto de Google Cloud.")
                st.error("2. **Permisos:** El service account podría no tener permisos de escritura. Ve a 'IAM y administración' en Google Cloud y asegúrate de que tenga el rol de 'Editor' o 'Usuario de Cloud Datastore'.")
                st.exception(e)
                st.stop()
            
            st.balloons()
            st.header("🎉 ¡Todas las pruebas pasaron! La conexión funciona.")
            st.info("Si todas las pruebas fueron exitosas, el formulario debería funcionar. Inténtalo de nuevo en la sección 'Formulario de Diagnóstico'.")
