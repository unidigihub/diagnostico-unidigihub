import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- Inicialización Firebase ---
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'diagnostico-unidigihub',
    })
db = firestore.client()

# --- Configuración de página ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")
st.image("logo_unidigihub.png", width=200)

# --- Inicializar variable de control ---
if "seccion_actual" not in st.session_state:
    st.session_state.seccion_actual = 1

# --- Sección 1 ---
def mostrar_seccion_1():
    st.title("Sección 1: Datos demográficos")
    st.markdown("""
    ### 👋 ¡Bienvenida y bienvenido al Diagnóstico UniDigiHub!
    Este autodiagnóstico tiene como propósito conocerte mejor para ayudarte a identificar tu punto de partida en el mundo digital.
    """)

    with st.form("form_datos_demograficos"):
        paises = [
            "México (Mēxihco)", "Colombia", "Chile", "Brasil", "Argentina",
            "Costa Rica", "Ecuador", "El Salvador", "Perú"
        ]
        pais = st.selectbox("1. ¿En qué país resides?", paises)
        departamento = st.text_input("2. Departamento o Estado donde vives")
        comunidad = st.text_input("3. Municipio o comunidad")
        edad = st.slider("4. ¿Cuál es tu edad?", min_value=15, max_value=90, step=1)
        genero = st.selectbox(
            "5. ¿Con qué género te identificas?",
            ["Femenino", "Masculino", "No binario", "Prefiero no decir", "Muxe (zapoteco)", "Otro"]
        )
        nivel_educativo = st.selectbox(
            "6. ¿Cuál es tu nivel educativo más alto alcanzado?",
            [
                "Primaria incompleta", "Primaria completa", "Secundaria",
                "Técnico", "Universitario 🎓", "Posgrado"
            ]
        )
        situacion_laboral = st.multiselect(
            "7. ¿Cuál es tu situación laboral actual?",
            [
                "Agricultura de subsistencia", "Empleo informal",
                "Estudiante", "Desempleado", "Trabajo remoto"
            ]
        )
        acceso_tecnologia = st.multiselect(
            "8. ¿Qué acceso tecnológico tienes actualmente?",
            [
                "📱 Teléfono móvil (sin internet)",
                "📱💻 Teléfono con internet",
                "💻 Computadora/Tablet",
                "📶 Internet estable en casa",
                "❌ Ninguno"
            ]
        )

        enviado = st.form_submit_button("Enviar sección 1")

    if enviado:
        doc = {
            "pais": pais,
            "departamento": departamento,
            "comunidad": comunidad,
            "edad": edad,
            "genero": genero,
            "nivel_educativo": nivel_educativo,
            "situacion_laboral": situacion_laboral,
            "acceso_tecnologia": acceso_tecnologia,
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        db.collection("diagnostico_seccion1").add(doc)

        st.success("✅ ¡Gracias! Sección 1 enviad
