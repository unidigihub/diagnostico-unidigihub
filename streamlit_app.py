import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time

# --- INICIALIZACIÓN DE FIREBASE (CON LA CORRECCIÓN FINAL) ---
def initialize_firebase():
    try:
        creds_from_secrets = st.secrets["firebase_credentials"]
        if isinstance(creds_from_secrets, str):
            creds_dict = json.loads(creds_from_secrets)
        else:
            creds_dict = dict(creds_from_secrets)
        
        # LA CORRECCIÓN CLAVE: Le decimos explícitamente cuál es el ID del proyecto.
        # Esto evita que el programa se confunda y busque el servidor de metadatos.
        project_id = creds_dict.get("project_id")
        
        cred = credentials.Certificate(creds_dict)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
            
    except Exception as e:
        st.error(f"Error CRÍTICO al conectar con la base de datos: {e}")
        st.stop()

initialize_firebase()
db = firestore.client()

# --- CONFIGURACIÓN DE PÁGINA Y ESTADO DE SESIÓN ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")

if "current_section" not in st.session_state:
    st.session_state.current_section = 1
if "firestore_doc_id" not in st.session_state:
    st.session_state.firestore_doc_id = None

# --- TÍTULO Y BARRA DE PROGRESO ---
st.title("📝 Diagnóstico UniDigiHub LATAM")
# --- BARRA DE PROGRESO CORREGIDA ---
total_sections = 7
progress_text = f"Progreso: Sección {st.session_state.current_section} de {total_sections}"
# Lógica para que la barra no muestre un progreso mayor al 100% si hay más secciones
current_progress = st.session_state.current_section / total_sections
st.progress(current_progress, text=progress_text)
st.markdown("---")


# --- SECCIÓN 1: DATOS DEMOGRÁFICOS ---
if st.session_state.current_section == 1:
    st.header("Sección 1: Datos Demográficos")
    # --- TEXTO DE BIENVENIDA CORREGIDO ---
    st.markdown("""
    ### 👋 ¡Bienvenida y bienvenido! 
    Este autodiagnóstico tiene como propósito conocerte mejor para ayudarte a identificar tu punto de partida en el mundo digital. A través de 7 secciones breves, exploraremos tus intereses, habilidades y contexto local para recomendarte una ruta de aprendizaje personalizada dentro de UniDigiHub.

    💡 **Tu participación nos permitirá diseñar experiencias formativas más inclusivas, útiles y adaptadas a tu realidad.**

    No se requiere experiencia previa. Solo responde con sinceridad 😊
    """)

    with st.form("form_s1"):
        paises = ["", "México (Mēxihco)", "Colombia", "Chile", "Brasil", "Argentina", "Costa Rica", "Ecuador", "El Salvador", "Perú"]
        st.selectbox("1. ¿En qué país resides?", paises, key="s1_pais")
        st.text_input("2. Departamento o Estado donde vives", key="s1_depto")
        st.text_input("3. Municipio o comunidad", key="s1_comunidad")
        # --- EDAD MÍNIMA CORREGIDA ---
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
            st.error(f"🚨 ¡Atención! Por favor, completa los siguientes campos para continuar: **{', '.join(campos_faltantes)}**.")
        else:
            doc_data = {
                "seccion1_demograficos": {
                    "pais": st.session_state.s1_pais, "departamento": st.session_state.s1_depto,
                    "comunidad": st.session_state.s1_comunidad, "edad": st.session_state.s1_edad,
                    "genero": st.session_state.s1_genero, "nivel_educativo": st.session_state.s1_educacion,
                    "situacion_laboral": st.session_state.s1_laboral, "acceso_tecnologia": st.session_state.s1_tecnologia,
                }, "timestamp_inicio": firestore.SERVER_TIMESTAMP
            }
            _, doc_ref = db.collection("respuestas_diagnostico_unificado").add(doc_data)
            st.session_state.firestore_doc_id = doc_ref.id
            st.session_state.current_section = 2
            st.success("✅ ¡Sección 1 guardada! Avanzando...")
            time.sleep(2)
            st.rerun()

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
            doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
            doc_ref.update({"seccion2_problematicas": {"problema_principal": st.session_state.s2_problema, "sectores_relacionados": st.session_state.s2_sectores, "impacto_escala": st.session_state.s2_impacto}})
            st.session_state.current_section = 3
            st.success("✅ ¡Sección 2 guardada! Avanzando...")
            time.sleep(1)
            st.rerun()

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
            doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
            doc_ref.update({"seccion3_intereses": {"sector_interes_principal": st.session_state.s3_sector_interes, "nivel_autodeclarado": nivel_autodeclarado}})
            st.session_state.current_section = 4
            st.success("✅ ¡Sección 3 guardada! Una más y terminamos.")
            time.sleep(1)
            st.rerun()

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
        doc_ref = db.collection("respuestas_diagnostico_unificado").document(st.session_state.firestore_doc_id)
        doc_ref.update({"seccion4_habilidades": {"autoevaluacion_tech": st.session_state.s4_autoeval_tech, "herramientas_conocidas": st.session_state.s4_herramientas, "respuesta_habilidad_blanda": st.session_state.s4_situacion_equipo[0]}, "timestamp_final": firestore.SERVER_TIMESTAMP, "estado": "Completado"})
        st.session_state.current_section = 5
        st.success("✅ ¡Diagnóstico finalizado! Calculando tu perfil...")
        time.sleep(2)
        st.rerun()

# --- LÓGICA PARA MOSTRAR LA PÁGINA FINAL ---
# Esta lógica ahora mostrará la página final cuando se hayan completado las 4 secciones que tenemos construidas.
# Y se detendrá allí hasta que construyamos las secciones 5, 6 y 7.
elif st.session_state.current_section == 5:
    st.header("🎉 ¡Diagnóstico Completado! 🎉")
    st.balloons()
    st.markdown("¡Muchas gracias por completar tu diagnóstico! Hemos guardado tus respuestas de forma segura.")
    st.info(f"Tu ID de registro único es: **{st.session_state.firestore_doc_id}**")
    st.markdown("El siguiente paso será analizar tus respuestas para darte un resultado. ¡Estamos trabajando en ello!")
