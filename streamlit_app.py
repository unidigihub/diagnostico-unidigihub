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

        # Puedes aquí decidir si avanzas a la siguiente sección o dejas que el usuario decida

        # Por ejemplo:

        # st.session_state.seccion_actual = 3

        # Cambiar a la siguiente sección

        st.session_state.seccion_actual = 2



# Función para mostrar Sección 3

def mostrar_seccion_3():

    st.title("Sección 3: Intereses profesionales")

    st.write("Queremos conocerte mejor para ayudarte a elegir un camino de aprendizaje adecuado.")



    with st.form("form_seccion3"):

        intereses = st.multiselect(

            "1. ¿Qué temas te interesan aprender o mejorar?",

            options=[

                "Transformación digital en mi comunidad",

                "Uso de tecnología para vender más",

                "Cuidado de la salud con tecnología",

                "Mejorar mi producción agrícola",

                "Energía limpia y sustentabilidad",

                "Finanzas personales y ahorro digital",

                "Desarrollo de aplicaciones o sitios web",

                "Otro"

            ]

        )

        motivaciones = st.text_area(

            "2. ¿Por qué te interesa aprender sobre estos temas?",

            placeholder="Ejemplo: mejorar mi negocio, conseguir empleo, ayudar a mi comunidad..."

        )

        tiempo_dedicacion = st.selectbox(

            "3. ¿Cuántas horas por semana podrías dedicar al aprendizaje digital?",

            ["1-2 horas", "3-5 horas", "6-10 horas", "Más de 10 horas"]

        )

        experiencia_digital = st.radio(

            "4. ¿Te consideras principiante o tienes experiencia previa usando herramientas digitales?",

            ["Principiante", "Algo de experiencia", "Avanzado"]

        )



        enviado = st.form_submit_button("Enviar sección 3")



    if enviado:

        doc = {

            "intereses": intereses,

            "motivaciones": motivaciones,

            "tiempo_dedicacion": tiempo_dedicacion,

            "experiencia_digital": experiencia_digital,

            "timestamp": firestore.SERVER_TIMESTAMP

        }

        db.collection("diagnostico_seccion3").add(doc)

        st.success("✅ ¡Gracias! Sección 3 enviada correctamente.")

        st.session_state.seccion_actual = 4



# Mostrar sección según variable de estado

if st.session_state.seccion_actual == 1:

    mostrar_seccion_1()

elif st.session_state.seccion_actual == 2:

    mostrar_seccion_2()

elif st.session_state.seccion_actual == 3:

    mostrar_seccion_3()





# Botones para navegar entre secciones manualmente (opcional)

col1, col2, col3 = st.columns([1,6,1])



with col1:

    if st.session_state.seccion_actual > 1:

        if st.button("⬅️ Sección anterior"):

            st.session_state.seccion_actual -= 1



with col3:

    if st.session_state.seccion_actual < 7:

        if st.button("Siguiente ➡️"):

            st.session_state.seccion_actual += 1
