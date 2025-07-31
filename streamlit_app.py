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

# --- Configuración página ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")
st.image("logo_unidigihub.png", width=200)

# --- Variables de color UniDigiHub ---
COLOR_AZUL = "#1E90FF"   # Innovación tecnológica
COLOR_VERDE = "#6DBE45"  # Desarrollo sostenible

# --- Estilos CSS globales para botones ---
st.markdown(f"""
<style>
div.stButton > button {{
    color: white;
    height: 500px;
    width: 500px;
    border-radius: 12px;
    border: none;
    font-size: 18px;
    font-weight: 300;
    cursor: pointer;
    transition: background-color 0.3s ease;
    background-color: {COLOR_AZUL};
}}
div.stButton > button:focus {{
    outline: none;
    box-shadow: 0 0 0 3px {COLOR_VERDE};
}}
div.stButton > button:hover {{
    filter: brightness(85%);
}}
</style>
""", unsafe_allow_html=True)

# --- Inicializar control de sección ---
if "seccion_actual" not in st.session_state:
    st.session_state.seccion_actual = 1

# --- Sección 1 ---
def mostrar_seccion_1():
    st.title("Sección 1: Datos demográficos")
    st.markdown("""
    ### 👋 ¡Bienvenida y bienvenido al Diagnóstico UniDigiHub!

    Este autodiagnóstico tiene como propósito conocerte mejor para ayudarte a identificar tu punto de partida en el mundo digital.

    💡 **Tu participación nos permitirá diseñar experiencias formativas más inclusivas, útiles y adaptadas a tu realidad.**

    No se requiere experiencia previa. Solo responde con sinceridad 😊
    """)

    with st.form("form_datos_demograficos"):
        paises = [
            "México (Mēxihco)", "Colombia", "Chile", "Brasil", "Argentina",
            "Costa Rica", "Ecuador", "El Salvador", "Perú"
        ]
        pais = st.selectbox("1. ¿En qué país resides?", paises)
        departamento = st.text_input("2. Departamento o Estado donde vives")
        comunidad = st.text_input("3. Municipio o comunidad")
        edad = st.slider("4. ¿Cuál es tu edad?", min_value=25, max_value=90, step=1)
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

        if "❌ Ninguno" in acceso_tecnologia:
            st.warning("🔔 No cuentas con tecnología. Recuerda que puedes solicitar contenido por SMS o radio.")
        elif "📱 Teléfono móvil (sin internet)" in acceso_tecnologia:
            st.info("📲 Se te priorizará para contenidos vía WhatsApp.")

        st.success("✅ ¡Gracias! Sección 1 enviada correctamente.")
        st.session_state.seccion_1_enviado = True

# --- Sección 2 ---
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
        st.session_state.seccion_2_enviado = True

# --- Mostrar sección según estado ---
if st.session_state.seccion_actual == 1:
    mostrar_seccion_1()
elif st.session_state.seccion_actual == 2:
    mostrar_seccion_2()
else:
    st.title("¡Gracias por completar el diagnóstico!")
    st.write("Pronto te contactaremos con tus resultados y rutas personalizadas.")

# --- Navegación (mejorada visualmente) ---
st.markdown("""<style>
.nav-button {
    display: inline-block;
    background-color: #1E90FF;
    color: white;
    padding: 10px 24px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    border-radius: 10px;
    text-align: center;
    margin: 10px;
}
.nav-button:disabled {
    background-color: #ccc;
}
</style>""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,6,1])
with col1:
    if st.session_state.seccion_actual > 1:
        if st.button("⬅️ Sección anterior"):
            st.session_state.seccion_actual -= 1

with col3:
    seccion_actual = st.session_state.seccion_actual
    seccion_enviada = st.session_state.get(f"seccion_{seccion_actual}_enviado", False)

    if seccion_enviada:
        if st.button("Siguiente ➡️"):
            st.session_state.seccion_actual += 1
    else:
        st.markdown('<button class="nav-button" disabled>Completa la sección</button>', unsafe_allow_html=True)
