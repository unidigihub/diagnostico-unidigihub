
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

# --- Título y bienvenida ---
st.title("Sección 1: Datos demográficos")

st.markdown("""
### 👋 ¡Bienvenida y bienvenido al Diagnóstico UniDigiHub!

Este autodiagnóstico tiene como propósito conocerte mejor para ayudarte a identificar tu punto de partida en el mundo digital. A través de 7 secciones breves, exploraremos tus intereses, habilidades y contexto local para recomendarte una ruta de aprendizaje personalizada dentro de UniDigiHub.

💡 **Tu participación nos permitirá diseñar experiencias formativas más inclusivas, útiles y adaptadas a tu realidad.**

No se requiere experiencia previa. Solo responde con sinceridad 😊
""")

with st.form("form_datos_demograficos"):
    # País con nombres indígenas
    paises = [
        "México (Mēxihco)", "Colombia", "Chile", "Brasil", "Argentina",
        "Costa Rica", "Ecuador", "El Salvador", "Perú"
    ]
    pais = st.selectbox("1. ¿En qué país resides?", paises)

    # Departamento / Estado (placeholder para integración futura con Google Places API)
    departamento = st.text_input("2. Departamento o Estado donde vives")

    # Municipio / Comunidad
    comunidad = st.text_input("3. Municipio o comunidad")

    # Edad
    edad = st.slider("4. ¿Cuál es tu edad?", min_value=22, max_value=90, step=1)

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
        # Cambiar a la siguiente sección
        st.session_state.seccion_actual = 2

# Función para mostrar Sección 2
def mostrar_seccion_2():
    st.title("Sección 2: Problemáticas locales")
    st.write("Por favor, responde estas preguntas sobre los desafíos que enfrenta tu comunidad.")

    with st.form("form_seccion2"):

        # 1. Problema principal (campo texto guiado)
        problema_principal = st.text_area(
            "1. Describe el problema principal que afecta a tu comunidad",
            placeholder='Ejemplo: "Sequía en cultivos", "Falta de acceso a servicios de salud", "Cortes frecuentes de energía"'
        )
        # Aquí podrías implementar sugerencias basadas en ubicación con integración futura Google Maps API

        # 2. Relación con sectores (selector múltiple con íconos)
        sectores = st.multiselect(
            "2. ¿Con qué sectores crees que se relaciona este problema?",
            options=[
                "Agricultura y tecnología",
                "Finanzas digitales",
                "Salud comunitaria",
                "Energía limpia"
            ]
        )
        # Puedes agregar íconos junto a cada opción con HTML/Markdown o librerías externas si lo deseas

        # 3. Impacto del problema (escala Likert + texto)
        impacto = st.slider(
            "3. ¿Cuál es el impacto del problema en tu comunidad?",
            min_value=1, max_value=5, value=3,
            format="%d (1= Bajo impacto, 5= Crítico)"
        )
        impacto_descripcion = st.text_area(
            "¿Cómo afecta este problema a tu comunidad?"
        )
        # En backend podrías usar análisis de sentimiento con Google Natural Language API para detectar urgencia

        # 4. Soluciones intentadas (checkbox + texto libre)
        soluciones = st.multiselect(
            "4. ¿Qué soluciones se han intentado para este problema?",
            options=[
                "Tecnología básica (ej: apps móviles)",
                "Métodos tradicionales",
                "Ninguna"
            ]
        )
        texto_soluciones = st.text_area(
            "Describe brevemente soluciones fallidas o exitosas"
        )
        # Aquí podrías usar NLP avanzado para clasificar comentarios

        # 5. Recursos disponibles (selector múltiple)
        recursos = st.multiselect(
            "5. ¿Qué recursos tiene tu comunidad para enfrentar este problema?",
            options=[
                "Acceso a internet",
                "Tierra cultivable",
                "Mano de obra",
                "Ninguno"
            ]
        )
        # Puedes agregar íconos a cada opción y hacer geomatching con BigQuery en backend

        enviado = st.form_submit_button("Enviar sección 2")

    if enviado:
        doc = {
            "problema_principal": problema_principal,
            "sectores": sectores,
            "impacto": impacto,
            "impacto_descripcion": impacto_descripcion,
            "soluciones": soluciones,
            "texto_soluciones": texto_soluciones,
            "recursos": recursos,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        db.collection("diagnostico_seccion2").add(doc)
        st.success("✅ ¡Gracias! Sección 2 enviada correctamente.")

