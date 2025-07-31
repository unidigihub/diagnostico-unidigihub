
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# --- Inicialización Firebase ---
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'diagnostico-unidigihub',
    })
db = firestore.client()

# --- Configuración página ---
st.set_page_config(page_title="Diagnóstico UniDigiHub – Sección 1", layout="centered")
st.image("logo_unidigihub.png", width=200)
st.title("Sección 1: Datos demográficos")

with st.form("form_datos_demograficos"):
    # País con nombres indígenas
    paises = [
        "México (Mēxihco)", "Colombia", "Chile", "Brasil", "Argentina",
        "Costa Rica", "Ecuador", "El Salvador", "Perú"
    ]
    pais = st.selectbox("1. ¿En qué país resides?", paises)

    # Departamento / Estado (placeholder para integración futura con Google Places API)
    departamento = st.text_input("2. Departamento o estado donde vives (sugerido por ubicación)")

    # Municipio / Comunidad
    comunidad = st.text_input("3. Municipio o comunidad")

    # Edad
    edad = st.slider("4. ¿Cuál es tu edad?", min_value=15, max_value=90, step=1)

    # Género
    genero = st.selectbox(
        "5. ¿Con qué género te identificas?",
        ["Femenino", "Masculino", "No binario", "Prefiero no decir", "Muxe (zapoteco)", "Otro"]
    )

    # Nivel educativo
    nivel_educativo = st.selectbox(
        "6. ¿Cuál es tu nivel educativo más alto alcanzado?",
        [
            "Primaria incompleta", "Primaria completa", "Secundaria",
            "Técnico", "Universitario 🎓", "Posgrado"
        ]
    )

    # Situación laboral
    situacion_laboral = st.multiselect(
        "7. ¿Cuál es tu situación laboral actual?",
        [
            "Agricultura de subsistencia", "Empleo informal",
            "Estudiante", "Desempleado", "Trabajo remoto"
        ]
    )

    # Acceso a tecnología
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

# --- Guardado en Firestore ---
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

    # Validación condicional de tecnología
    if "❌ Ninguno" in acceso_tecnologia:
        st.warning("🔔 No cuentas con tecnología. Recuerda que puedes solicitar contenido por SMS o radio.")
    elif "📱 Teléfono móvil (sin internet)" in acceso_tecnologia:
        st.info("📲 Se te priorizará para contenidos vía WhatsApp.")

    db.collection("diagnostico_seccion1").add(doc)
    st.success("✅ ¡Gracias! Sección 1 enviada correctamente.")

    # Sugerencia para navegación
    st.markdown("👉 Haz clic en **Siguiente** para continuar a la Sección 2.")
