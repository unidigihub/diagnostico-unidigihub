import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json # Necesitamos este "traductor"
import time

# --- INICIALIZACIÓN DE FIREBASE (LA VERSIÓN QUE SÍ FUNCIONA) ---
def initialize_firebase():
    """
    Inicializa Firebase de forma segura.
    Esta versión incluye el "organizador" (json.loads) para arreglar el error.
    """
    try:
        creds_from_secrets = st.secrets["firebase_credentials"]

        # El "Organizador": si la receta es un párrafo (string), la convierte en lista (dict)
        if isinstance(creds_from_secrets, str):
            creds_dict = json.loads(creds_from_secrets)
        else:
            creds_dict = dict(creds_from_secrets)
        
        cred = credentials.Certificate(creds_dict)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        st.stop()

initialize_firebase()
db = firestore.client()

# --- CONFIGURACIÓN DE PÁGINA Y ESTADO DE SESIÓN ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")

# st.image("logo_unidigihub.png", width=200) # Descomenta si tienes un logo

if "current_section" not in st.session_state:
    st.session_state.current_section = 1
if "firestore_doc_id" not in st.session_state:
    st.session_state.firestore_doc_id = None

# --- TÍTULO Y BARRA DE PROGRESO ---
st.title("📝 Diagnóstico UniDigiHub LATAM")
total_sections = 5
progress_text = f"Progreso: Sección {st.session_state.current_section} de {total_sections}"
st.progress(st.session_state.current_section / total_sections, text=progress_text)
st.markdown("---")


# --- SECCIÓN 1: DATOS DEMOGRÁFICOS ---
if st.session_state.current_section == 1:
    st.header("Sección 1: Datos Demográficos")
    st.markdown("### 👋 ¡Bienvenida y bienvenido! \n Este diagnóstico nos ayudará a conocerte para personalizar tu ruta de aprendizaje.")

    with st.form("form_s1"):
        pais = st.selectbox("1. ¿En qué país resides?", ["", "México", "Colombia", "Chile", "Brasil", "Argentina", "Costa Rica", "Ecuador", "El Salvador", "Perú"])
        departamento = st.text_input("2. Departamento o Estado donde vives")
        edad = st.slider("3. ¿Cuál es tu edad?", 25, 90, 25)
        genero = st.selectbox("4. ¿Con qué género te identificas?", ["", "Femenino", "Masculino", "No binario", "Prefiero no decir", "Muxe (zapoteco)", "Otro"])
        
        submitted_s1 = st.form_submit_button("Guardar y Continuar")

    if submitted_s1:
        if not all([pais, departamento, genero]):
            st.warning("Por favor, completa todos los campos obligatorios.")
        else:
            doc_data = {
                "seccion1_demograficos": { "pais": pais, "departamento": departamento, "edad": edad, "genero": genero, },
                "timestamp_inicio": firestore.SERVER_TIMESTAMP
            }
            _, doc_ref = db.collection("respuestas_diagnostico_unificado").add(doc_data)
            st.session_state.firestore_doc_id = doc_ref.id
            st.session_state.current_section = 2
            st.success("✅ ¡Sección 1 guardada! Avanzando...")
            time.sleep(1)
            st.rerun()

# --- SECCIÓN 2: PROBLEMÁTICAS LOCALES ---
elif st.session_state.current_section == 2:
    st.header("Sección 2: Problemáticas Locales")
    with st.form("form_s2"):
        problema_principal = st.text_area("1. Describe el problema principal que afecta a tu comunidad", placeholder='Ej: "Sequía en cultivos", "Falta de acceso a servicios de salud"...')
        sectores = st.multiselect("2. ¿Con qué sectores se relaciona este problema?", ["Agricultura y tecnología", "Finanzas digitales", "Salud comunitaria", "Energía limpia"])
        impacto = st.slider("3. Impacto del problema en tu comunidad (1=Bajo, 5=Crítico)", 1, 5, 3)
        submitted_s2 = st.form_submit_button("Guardar y Continuar")

    if submitted_s2:
        if not problema_principal: st.warning("Por favor, describe el problema principal.")
        else:
            doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
            doc_ref.update({ "seccion2_problematicas": { "problema_principal": problema_principal, "sectores_relacionados": sectores, "impacto_escala": impacto } })
            st.session_state.current_section = 3
            st.success("✅ ¡Sección 2 guardada! Avanzando...")
            time.sleep(1)
            st.rerun()

# --- SECCIÓN 3: INTERESES PROFESIONALES ---
elif st.session_state.current_section == 3:
    st.header("Sección 3: Intereses Profesionales")
    with st.form("form_s3"):
        sector_interes = st.selectbox("1. ¿Cuál de estos sectores te atrae más?", ["", "AgriTech (Agricultura)", "FinTech (Finanzas)", "HealthTech (Salud)", "Energías Renovables"])
        experiencia_previa = st.radio("2. ¿Cuál es tu nivel de experiencia en proyectos tecnológicos?", ["**UniExplorador** (Ninguna o baja experiencia)", "**UniCreador** (Experiencia básica, participé en proyectos)", "**UniVisionario** (Experiencia avanzada, lideré proyectos)"])
        submitted_s3 = st.form_submit_button("Guardar y Continuar")
        
    if submitted_s3:
        if not sector_interes: st.warning("Por favor, selecciona un sector de interés.")
        else:
            nivel_autodeclarado = experiencia_previa.split("**")[1]
            doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
            doc_ref.update({ "seccion3_intereses": { "sector_interes_principal": sector_interes, "nivel_autodeclarado": nivel_autodeclarado } })
            st.session_state.current_section = 4
            st.success("✅ ¡Sección 3 guardada! Una más y terminamos.")
            time.sleep(1)
            st.rerun()

# --- SECCIÓN 4: HABILIDADES TÉCNICAS Y BLANDAS ---
elif st.session_state.current_section == 4:
    st.header("Sección 4: Habilidades y Competencias")
    with st.form("form_s4"):
        st.subheader("Autoevaluación de Habilidades Técnicas")
        autoevaluacion_tech = st.slider("1. En una escala de 1 (Nada) a 5 (Mucho), ¿qué tan cómodo te sientes con la programación o el análisis de datos?", 1, 5, 2)
        
        st.subheader("Herramientas Conocidas")
        herramientas = st.multiselect("2. Marca las herramientas o conceptos que conozcas (no importa el nivel)", ["Sensores IoT", "Drones", "Plataformas de pago (ej. Stripe)", "Blockchain", "Apps de Telemedicina", "Software de simulación de energía"])

        st.subheader("Habilidades Blandas")
        situacion_equipo = st.radio(
            "3. Imagina que tu equipo discute sobre qué método usar en un proyecto y no se ponen de acuerdo. ¿Qué harías?",
            [
                "A) Dejo que otros decidan para no generar conflicto.",
                "B) Busco un consenso escuchando a todos para llegar a un acuerdo.",
                "C) Analizo los datos de cada propuesta y presento la solución más lógica para que el equipo mejore."
            ]
        )
        submitted_s4 = st.form_submit_button("Finalizar Diagnóstico")

    if submitted_s4:
        doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
        doc_ref.update({
            "seccion4_habilidades": {
                "autoevaluacion_tech": autoevaluacion_tech,
                "herramientas_conocidas": herramientas,
                "respuesta_habilidad_blanda": situacion_equipo[0] # Guardamos solo la letra (A, B, o C)
            },
            "timestamp_final": firestore.SERVER_TIMESTAMP,
            "estado": "Completado"
        })
        st.session_state.current_section = 5
        st.success("✅ ¡Diagnóstico finalizado! Calculando tu perfil...")
        time.sleep(2)
        st.rerun()

# --- SECCIÓN FINAL: RESULTADOS (EN CONSTRUCCIÓN) ---
elif st.session_state.current_section == 5:
    st.header("🎉 ¡Diagnóstico Completado! 🎉")
    st.balloons()
    st.markdown("¡Muchas gracias por completar tu diagnóstico! Hemos guardado tus respuestas de forma segura.")
    st.info(f"Tu ID de registro único es: **{st.session_state.firestore_doc_id}**")
    st.markdown("El siguiente paso será analizar tus respuestas para darte un resultado. ¡Estamos trabajando en ello!")
