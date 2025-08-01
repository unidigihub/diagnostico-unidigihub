import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- INICIALIZACIÓN DE FIREBASE (MÉTODO RECOMENDADO) ---
# Este método usa un archivo de credenciales, que es más seguro y explícito.
# Asegúrate de tener tu archivo "firebase-credentials.json" en la misma carpeta.
try:
    cred = credentials.Certificate("firebase-credentials.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
except FileNotFoundError:
    st.error("Error: No se encontró el archivo 'firebase-credentials.json'. Asegúrate de que esté en el directorio correcto.")
    st.stop()

db = firestore.client()

# --- CONFIGURACIÓN DE PÁGINA Y ESTADO DE SESIÓN ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")

# st.image("logo_unidigihub.png", width=200) # Descomenta si tienes un logo

# Inicializar variables para controlar el flujo del formulario
if "current_section" not in st.session_state:
    st.session_state.current_section = 1
if "firestore_doc_id" not in st.session_state:
    st.session_state.firestore_doc_id = None

# --- TÍTULO Y BARRA DE PROGRESO ---
st.title("📝 Diagnóstico UniDigiHub LATAM")
total_sections = 5 # Ajusta este número al total de secciones planeadas
progress_text = f"Progreso: Sección {st.session_state.current_section} de {total_sections}"
st.progress(st.session_state.current_section / total_sections, text=progress_text)
st.markdown("---")


# --- SECCIÓN 1: DATOS DEMOGRÁFICOS ---
if st.session_state.current_section == 1:
    st.header("Sección 1: Datos Demográficos")
    st.markdown("### 👋 ¡Bienvenida y bienvenido! \n Este diagnóstico nos ayudará a conocerte para personalizar tu ruta de aprendizaje.")

    with st.form("form_s1"):
        # Preguntas de la sección 1, tomadas de los documentos de requerimientos
        pais = st.selectbox("1. ¿En qué país resides?", ["", "México", "Colombia", "Chile", "Brasil", "Argentina", "Costa Rica", "Ecuador", "El Salvador", "Perú"])
        departamento = st.text_input("2. Departamento o Estado donde vives")
        edad = st.slider("3. ¿Cuál es tu edad?", 15, 90, 25)
        genero = st.selectbox("4. ¿Con qué género te identificas?", ["", "Femenino", "Masculino", "No binario", "Prefiero no decir", "Muxe (zapoteco)", "Otro"])
        nivel_educativo = st.selectbox("5. Máximo nivel educativo", ["", "Primaria incompleta", "Primaria completa", "Secundaria", "Técnico", "Universitario 🎓", "Posgrado"])
        situacion_laboral = st.multiselect("6. Situación laboral actual", ["Agricultura de subsistencia", "Empleo informal", "Estudiante", "Desempleado", "Trabajo remoto"])
        acceso_tecnologia = st.multiselect("7. ¿Qué acceso tecnológico tienes?", ["📱 Teléfono móvil (sin internet)", "📱 Teléfono con internet", "💻 Computadora/Tablet", "📶 Internet estable en casa", "❌ Ninguno"])
        
        submitted_s1 = st.form_submit_button("Guardar y Continuar")

    if submitted_s1:
        if not all([pais, departamento, genero, nivel_educativo]):
            st.warning("Por favor, completa todos los campos obligatorios.")
        else:
            # Crea un NUEVO documento en Firestore
            doc_data = {
                "seccion1_demograficos": {
                    "pais": pais, "departamento": departamento, "edad": edad, "genero": genero,
                    "nivel_educativo": nivel_educativo, "situacion_laboral": situacion_laboral,
                    "acceso_tecnologia": acceso_tecnologia,
                },
                "timestamp_inicio": firestore.SERVER_TIMESTAMP
            }
            _, doc_ref = db.collection("respuestas_diagnostico_unificado").add(doc_data)
            st.session_state.firestore_doc_id = doc_ref.id # Guarda el ID del documento
            st.session_state.current_section = 2 # Avanza a la siguiente sección
            
            st.success("✅ ¡Sección 1 guardada! Avanzando a la siguiente sección...")
            time.sleep(2)
            st.rerun()


# --- SECCIÓN 2: PROBLEMÁTICAS LOCALES ---
elif st.session_state.current_section == 2:
    st.header("Sección 2: Problemáticas Locales")
    st.markdown("Cuéntanos sobre los desafíos en tu comunidad para enfocar tu aprendizaje en soluciones reales.")

    with st.form("form_s2"):
        # Preguntas de la sección 2
        problema_principal = st.text_area("1. Describe el problema principal que afecta a tu comunidad", placeholder='Ej: "Sequía en cultivos", "Falta de acceso a servicios de salud"...')
        sectores = st.multiselect("2. ¿Con qué sectores se relaciona este problema?", ["Agricultura y tecnología", "Finanzas digitales", "Salud comunitaria", "Energía limpia"])
        impacto = st.slider("3. Impacto del problema en tu comunidad (1=Bajo, 5=Crítico)", 1, 5, 3)
        
        submitted_s2 = st.form_submit_button("Guardar y Continuar")

    if submitted_s2:
        if not problema_principal:
            st.warning("Por favor, describe el problema principal.")
        else:
            # ACTUALIZA el documento existente con los datos de esta sección
            doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
            doc_ref.update({
                "seccion2_problematicas": {
                    "problema_principal": problema_principal, "sectores_relacionados": sectores, "impacto_escala": impacto,
                }
            })
            st.session_state.current_section = 3
            
            st.success("✅ ¡Sección 2 guardada! Avanzando...")
            time.sleep(2)
            st.rerun()


# --- SECCIÓN 3: INTERESES PROFESIONALES ---
elif st.session_state.current_section == 3:
    st.header("Sección 3: Intereses Profesionales")
    st.markdown("Ayúdanos a entender tus metas y tu experiencia para asignarte un nivel inicial.")

    with st.form("form_s3"):
        # Preguntas de la sección 3
        sector_interes = st.selectbox(
            "1. ¿Cuál de estos sectores te atrae más para desarrollar un proyecto?",
            ["", "AgriTech (Agricultura)", "FinTech (Finanzas)", "HealthTech (Salud)", "Energías Renovables"],
            help="Este será tu cluster principal."
        )
        experiencia_previa = st.radio(
            "2. ¿Cuál es tu nivel de experiencia en proyectos tecnológicos o digitales?",
            ["**UniExplorador** (Ninguna o baja experiencia, quiero aprender desde cero)", "**UniCreador** (Tengo experiencia básica, he participado en algunos proyectos)", "**UniVisionario** (Tengo experiencia avanzada, he liderado o desarrollado proyectos con resultados)"],
            index=0
        )
        
        submitted_s3 = st.form_submit_button("Guardar y Continuar")
        
    if submitted_s3:
        if not sector_interes:
            st.warning("Por favor, selecciona un sector de interés.")
        else:
            # Extrae solo el nombre del nivel para guardarlo limpiamente
            nivel_autodeclarado = experiencia_previa.split("**")[1]

            # ACTUALIZA el documento existente
            doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
            doc_ref.update({
                "seccion3_intereses": {
                    "sector_interes_principal": sector_interes, "nivel_autodeclarado": nivel_autodeclarado,
                }
            })
            st.session_state.current_section = 4

            st.success("✅ ¡Sección 3 guardada! Casi terminamos.")
            time.sleep(2)
            st.rerun()

# --- SECCIÓN FINAL ---
elif st.session_state.current_section > 3: # Se mostrará cuando se completen las secciones anteriores
    st.header("🎉 ¡Diagnóstico Completado! 🎉")
    st.balloons()
    st.markdown("¡Muchas gracias por completar tu diagnóstico! Hemos guardado tus respuestas de forma segura.")
    st.info(f"Tu ID de registro único es: **{st.session_state.firestore_doc_id}**")
    st.markdown("En breve, el equipo de UniDigiHub se pondrá en contacto contigo con los siguientes pasos.")
