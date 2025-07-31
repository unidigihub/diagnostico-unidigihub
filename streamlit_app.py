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

st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")
st.image("logo_unidigihub.png", width=200)

# Inicializar variable para control de secciones
if "seccion_actual" not in st.session_state:
    st.session_state.seccion_actual = 1

# Función para mostrar Sección 1
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

        st.success("✅ ¡Gracias! Sección 1 enviada correctamente.")
        # Cambiar a la siguiente sección
        st.session_state.seccion_actual = 2

# Función para mostrar Sección 2
def mostrar_seccion_2():
    st.title("Sección 2: Problemáticas locales")
    st.write("Por favor, responde estas preguntas sobre los desafíos que enfrenta tu comunidad.")

    with st.form("form_seccion2"):
        problema_principal = st.text_area(
            "1. Describe el problema principal que afecta a tu comunidad",
            placeholder='Ejemplo: "Sequía en cultivos", "Falta de acceso a servicios de salud", "Cortes frecuentes de energía"'
        )
        sectores = st.multiselect(
            "2. ¿Con qué sectores crees que se relaciona este problema?",
            options=[
                "Agricultura y tecnología",
                "Finanzas digitales",
                "Salud comunitaria",
                "Energía limpia"
            ]
        )
        impacto = st.slider(
            "3. ¿Cuál es el impacto del problema en tu comunidad?",
            min_value=1, max_value=5, value=3,
            format="%d (1= Bajo impacto, 5= Crítico)"
        )
        impacto_descripcion = st.text_area(
            "¿Cómo afecta este problema a tu comunidad?"
        )
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
        recursos = st.multiselect(
            "5. ¿Qué recursos tiene tu comunidad para enfrentar este problema?",
            options=[
                "Acceso a internet",
                "Tierra cultivable",
                "Mano de obra",
                "Ninguno"
            ]
        )

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
       
import streamlit as st
from firebase_admin import firestore

# Inicialización de la variable de sesión
if "seccion_actual" not in st.session_state:
    st.session_state.seccion_actual = 3

# ----------------------------
# SECCIÓN 3: Intereses profesionales
# ----------------------------
def mostrar_seccion_3():
    st.title("Sección 3: Intereses profesionales")
    st.write("Queremos conocerte mejor para ayudarte a diseñar una ruta de aprendizaje personalizada.")

    with st.form("form_seccion3"):
        # 1. Sector de interés
        sector = st.selectbox(
            "1. ¿Cuál es el sector que más te interesa?",
            ["🌱 AgriTech", "💰 FinTech", "🏥 HealthTech", "🌞 Energías Renovables"]
        )

        # 2. Nivel de experiencia
        nivel = st.radio(
            "2. ¿Qué nivel de experiencia tienes?",
            ["🔍 UniExplorador (Ninguna/baja experiencia)", 
             "🛠️ UniCreador (Experiencia básica en proyectos)", 
             "🚀 UniVisionario (Experiencia avanzada con resultados)"]
        )
        descripcion_exp = st.text_area("Describe tu experiencia (Ejemplo: curso básico de IoT):")

        # 3. Áreas de interés (según nivel)
        st.write("3. Selecciona tus áreas de interés:")
        if "UniExplorador" in nivel:
            areas = st.multiselect(
                "Opciones para UniExplorador",
                ["Introducción a IoT", "Conceptos básicos de blockchain"]
            )
        elif "UniCreador" in nivel:
            areas = st.multiselect(
                "Opciones para UniCreador",
                ["Diseño de apps AgriTech", "Análisis de datos en salud"]
            )
        elif "UniVisionario" in nivel:
            areas = st.multiselect(
                "Opciones para UniVisionario",
                ["Optimización de redes neuronales", "Sistemas autónomos de energía"]
            )
        else:
            areas = []

        # 4. Nivel de profundidad deseado
        complejidad = st.slider(
            "4. ¿Qué nivel de profundidad deseas alcanzar?",
            0, 10, 3,
            help="0 = Básico (Ej: Aprender a usar sensores), 10 = Avanzado (Ej: Desarrollar un MVP escalable)"
        )
        if complejidad >= 8 and "UniExplorador" in nivel:
            st.warning("⚠️ El nivel seleccionado es muy avanzado para un perfil Explorador. Considera ajustar tu nivel o tomar una formación básica primero.")

        # 5. Proyecto deseado
        proyecto = st.text_area(
            "5. Describe una idea de proyecto que te gustaría desarrollar.\n\nEjemplos:\n- UniExplorador: Crear un huerto con sensores básicos\n- UniCreador: Automatizar riego con Arduino\n- UniVisionario: Modelar una red inteligente de energía solar"
        )

        enviado = st.form_submit_button("Enviar sección 3")

    if enviado:
        doc = {
            "sector_interes": sector,
            "nivel_experiencia": nivel,
            "descripcion_experiencia": descripcion_exp,
            "areas_interes": areas,
            "complejidad_deseada": complejidad,
            "proyecto_deseado": proyecto,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        db.collection("diagnostico_seccion3").add(doc)
        st.success("✅ ¡Gracias! Has completado la Sección 3.")
        st.session_state.seccion_actual = 4

# ----------------------------
# --- SECCIÓN 4: HABILIDADES TÉCNICAS ---
# ----------------------------

st.header("4. Habilidades técnicas")

# 1. Autoevaluación general
st.subheader("1. ¿Qué tanto manejas herramientas tecnológicas en tu sector de interés?")
tecnologia = st.slider("Califica tu nivel de manejo tecnológico:", 1, 5, 3,
                       format="%d", help="1 = Nulo, 3 = Intermedio, 5 = Experto")
emoji_map = {1: "😕", 2: "😐", 3: "🙂", 4: "😀", 5: "😃"}
st.markdown(f"**Nivel seleccionado:** {tecnologia} {emoji_map[tecnologia]}")

# 2. Herramientas utilizadas (según sector)
st.subheader("2. ¿Qué herramientas has utilizado?")
cluster = st.session_state.get("sector_interes", "FinTech")  # Asegúrate de que este valor esté guardado

herramientas_opciones = {
    "AgriTech": ["🌾 Sensores IoT", "🚁 Drones agrícolas", "🧠 FarmBot"],
    "FinTech": ["⛓️ Blockchain (Ethereum)", "💳 APIs de pago (Stripe)", "📈 Herramientas de análisis financiero"],
    "HealthTech": ["🩺 Telemedicina", "⌚ Wearables", "📊 Software de monitoreo de salud"],
    "Energías Renovables": ["🔋 PVsyst", "⚡ Gestores de red eléctrica", "🧮 Simuladores energéticos"]
}
herramientas_seleccionadas = st.multiselect("Selecciona las que has usado:",
                                             opciones := herramientas_opciones.get(cluster, []))

# 3. Ejercicio práctico adaptativo
st.subheader("3. Responde una pregunta técnica")
nivel = st.session_state.get("nivel_experiencia", "UniExplorador")  # Asegúrate de que este valor esté guardado

if nivel == "UniExplorador":
    pregunta = "¿Qué es un sensor IoT?"
    opciones = ["Dispositivo que mide variables físicas", "Aplicación para enviar mensajes", "Una red social"]
    respuesta = st.radio(pregunta, opciones)
elif nivel == "UniCreador":
    respuesta = st.text_area("Describa cómo configuraría un sistema de riego con Arduino")
else:  # UniVisionario
    respuesta = st.text_area("Proponga un algoritmo para optimizar el consumo energético en una red solar")

# 4. Certificaciones
st.subheader("4. ¿Tienes certificaciones técnicas?")
certificaciones = st.selectbox("Selecciona una opción", ["Ninguna", "Cursos en línea", "Certificaciones técnicas"])
if certificaciones != "Ninguna":
    certificado_url = st.text_input("Agrega un enlace al certificado (Google Drive, etc.)")

# 5. Proyectos realizados
st.subheader("5. Cuéntanos sobre algún proyecto técnico que hayas hecho")
proyecto = st.text_area("Ejemplo: Automatización de riego con sensores y app móvil.")

# Guardar datos de la sección 4 en el estado de sesión
st.session_state["seccion_4"] = {
    "nivel_tecnologico": tecnologia,
    "herramientas": herramientas_seleccionadas,
    "respuesta_practica": respuesta,
    "certificaciones": certificaciones,
    "certificado_url": certificado_url if certificaciones != "Ninguna" else None,
    "proyecto": proyecto
}

if st.session_state.seccion_actual == 1:
    mostrar_seccion_1()
elif st.session_state.seccion_actual == 2:
    mostrar_seccion_2()
elif st.session_state.seccion_actual == 3:
    mostrar_seccion_3()

# ----------------------------
# Navegación entre secciones (opcional)
# ----------------------------
col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    if st.session_state.seccion_actual > 1:
        if st.button("⬅️ Sección anterior"):
            st.session_state.seccion_actual -= 1

with col3:
    if st.session_state.seccion_actual < 7:
        if st.button("Siguiente ➡️"):
            st.session_state.seccion_actual += 1
