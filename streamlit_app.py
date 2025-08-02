import streamlit as st
import firebase_admin
from firebase_admin import credentials
import json
import time
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import datetime

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
PROJECT_ID = "diagnostico-unidigihub"
creds_dict = None

def get_credentials():
    global creds_dict
    if creds_dict: return creds_dict
    try:
        creds_from_secrets = st.secrets["firebase_credentials"]
        creds_dict = dict(creds_from_secrets) if not isinstance(creds_from_secrets, str) else json.loads(creds_from_secrets)
        return creds_dict
    except Exception as e:
        st.error(f"Error CRÍTICO al leer las credenciales: {e}")
        st.stop()

def get_access_token():
    try:
        creds_info = get_credentials()
        scopes = ['https://www.googleapis.com/auth/datastore']
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)
        if not creds.token:
            creds.refresh(Request())
        return creds.token
    except Exception as e:
        st.error("No se pudo obtener el token de acceso para Firestore.")
        st.exception(e)
        return None

def format_value(value):
    if isinstance(value, str):
        try:
            datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
            return {"timestampValue": value}
        except (ValueError, TypeError):
            return {"stringValue": value}
    if isinstance(value, int) or isinstance(value, float): return {"integerValue": str(int(value))}
    if isinstance(value, list):
        if not value: return {"arrayValue": {}}
        else: return {"arrayValue": {"values": [{"stringValue": str(v)} for v in value]}}
    if isinstance(value, dict):
        return {"mapValue": {"fields": {k: format_value(v) for k, v in value.items()}}}
    return {}

def save_data_rest(collection, data):
    access_token = get_access_token()
    if not access_token: return False, None, "Fallo en obtener token"
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    firestore_data = {"fields": {key: format_value(value) for key, value in data.items()}}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(firestore_data))
        response.raise_for_status()
        doc_name = response.json().get("name", "").split("/")[-1]
        return True, doc_name, None
    except Exception as e:
        return False, None, e

def update_data_rest(full_doc_path, data_to_update):
    access_token = get_access_token()
    if not access_token: return False, "Fallo en obtener token"
    update_mask = '&'.join([f'updateMask.fieldPaths={key}' for key in data_to_update.keys()])
    url = f"https://firestore.googleapis.com/v1/{full_doc_path}?{update_mask}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    firestore_data = {"fields": {key: format_value(value) for key, value in data_to_update.items()}}
    try:
        response = requests.patch(url, headers=headers, data=json.dumps(firestore_data))
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, e

# --- CONFIGURACIÓN DE PÁGINA Y ESTADO ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")
if "current_section" not in st.session_state: st.session_state.current_section = 1
if "firestore_doc_path" not in st.session_state: st.session_state.firestore_doc_path = None

st.title("📝 Diagnóstico UniDigiHub LATAM")
total_sections = 5
progress_text = f"Progreso: Sección {st.session_state.current_section} de {total_sections}"
st.progress(st.session_state.current_section / total_sections if st.session_state.current_section <= total_sections else 1.0, text=progress_text)
st.markdown("---")

# --- SECCIÓN 1: DATOS DEMOGRÁFICOS ---
if st.session_state.current_section == 1:
    st.header("Sección 1: ¡Hola! Queremos conocerte")
    st.markdown("Para empezar, cuéntanos un poco sobre ti. Esto nos ayuda a entender mejor tu contexto.")
    with st.form("form_s1"):
        st.selectbox("1. ¿País en que naciste?", ["", "México", "Colombia", "Chile", "Brasil", "Argentina", "Costa Rica", "Perú", "Ecuador"], key="s1_pais")
        st.text_input("2. Departamento o Estado", key="s1_depto")
        st.text_input("3. Municipio o comunidad en el que vives", key="s1_comunidad")
        st.slider("4. ¿Cuál es tu edad?", min_value=25, max_value=90, value=25, step=1, key="s1_edad")
        st.selectbox("5. ¿Con qué género te identificas?", ["", "Femenino", "Masculino", "No binario", "Prefiero no decir"], key="s1_genero")
        st.selectbox("6. ¿Cuál es tu último nivel educativo?", ["", "Primaria incompleta", "Primaria completa", "Secundaria", "Técnico", "Universitario", "Posgrado"], key="s1_educacion")
        st.selectbox("7. ¿Cuál es tu situación laboral actual?", ["", "Asalariado/a", "Trabajador por cuenta propia", "Trabajador familiar no remunerado", "Desempleado", "Miembro de cooperativa de productores", "Empleador (Dueño de negocio con empleados)"], key="s1_laboral")
        st.multiselect("8. ¿A qué tipo de tecnología tienes acceso?", ["Teléfono móvil (sin internet)", "Teléfono con internet", "Computadora/Tablet con internet", "Computadora/Tablet (sin internet)", "Internet estable en casa", "Ninguno"], key="s1_tecnologia")
        submitted_s1 = st.form_submit_button("Guardar y Continuar")
    if submitted_s1:
        campos_obligatorios = {"País": st.session_state.s1_pais, "Departamento o Estado": st.session_state.s1_depto, "Municipio o comunidad": st.session_state.s1_comunidad}
        campos_faltantes = [nombre for nombre, valor in campos_obligatorios.items() if not valor]
        if campos_faltantes: st.error(f"🚨 Por favor, completa los siguientes campos: **{', '.join(campos_faltantes)}**.")
        else:
            doc_data = {"seccion1_demograficos": {"pais": st.session_state.s1_pais, "departamento": st.session_state.s1_depto, "comunidad": st.session_state.s1_comunidad, "edad": st.session_state.s1_edad, "genero": st.session_state.s1_genero, "nivel_educativo": st.session_state.s1_educacion, "situacion_laboral": st.session_state.s1_laboral, "acceso_tecnologia": st.session_state.s1_tecnologia}, "timestamp_inicio": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            success, doc_id, error = save_data_rest("respuestas_diagnostico_unificado", doc_data)
            if success:
                st.session_state.firestore_doc_path = f"projects/{PROJECT_ID}/databases/(default)/documents/respuestas_diagnostico_unificado/{doc_id}"
                st.session_state.current_section = 2
                st.success("✅ ¡Sección 1 guardada! Avanzando..."); time.sleep(2); st.rerun()
            else: st.error("Error al guardar los datos."); st.exception(error)

# --- SECCIÓN 2: PROBLEMÁTICAS LOCALES ---
elif st.session_state.current_section == 2:
    st.header("Sección 2: Tu Entorno")
    st.markdown("Ahora, cuéntanos sobre los desafíos y recursos de tu comunidad. Esto es clave para encontrar soluciones con propósito.")
    with st.form("form_s2"):
        st.text_area("1. Describe el problema más importante en tu comunidad.", help="Ej: Se pierden las cosechas, no hay médico cerca, cortes de luz.", key="s2_problema")
        st.selectbox("2. ¿Con cuál de estas áreas se relaciona ese problema?", ["", "Agricultura y tecnología", "Finanzas digitales", "Salud comunitaria", "Energía limpia"], key="s2_sector_problema")
        st.slider("3. ¿Qué tan grande es el impacto de este problema? (1=Bajo, 5=Crítico)", 1, 5, 3, key="s2_impacto")
        st.text_area("4. ¿Cómo afecta este problema a tu comunidad?", key="s2_impacto_desc")
        st.multiselect("5. ¿Qué recursos sí hay en tu comunidad?", ["Acceso a internet", "Computadores", "Tierra cultivable", "Mano de obra", "Ninguno"], key="s2_recursos")
        submitted_s2 = st.form_submit_button("Guardar y Continuar")
    if submitted_s2:
        data_to_update = {"seccion2_problematicas": {"problema_principal": st.session_state.s2_problema, "sector_relacionado": st.session_state.s2_sector_problema, "impacto_escala": st.session_state.s2_impacto, "impacto_descripcion": st.session_state.s2_impacto_desc, "recursos_disponibles": st.session_state.s2_recursos}}
        success, error = update_data_rest(st.session_state.firestore_doc_path, data_to_update)
        if success: st.session_state.current_section = 3; st.success("✅ ¡Sección 2 guardada!"); time.sleep(1); st.rerun()
        else: st.error("Error al actualizar los datos."); st.exception(error)

# --- SECCIÓN 3: INTERESES PROFESIONALES ---
elif st.session_state.current_section == 3:
    st.header("Sección 3: Tus Intereses")
    st.markdown("Queremos saber qué te motiva y qué te gustaría lograr. ¡Esto nos ayudará a definir tu camino!")
    with st.form("form_s3"):
        st.selectbox("1. ¿Qué sector te interesa más para desarrollar una solución?", ["", "Agricultura, alimentos o naturaleza", "Dinero, negocios o emprendimiento", "Salud y bienestar", "Energía, medio ambiente o cambio climático"], key="s3_sector_interes")
        st.selectbox("2. ¿Qué tan cerca has estado de resolver un problema en ese sector?", ["", "He pensado en el problema, pero no sé por dónde empezar.", "Nunca lo he intentado, pero me gustaría aprender cómo.", "He intentado resolverlo por mi cuenta o con herramientas básicas.", "Ya he trabajado con otras personas o grupos para resolverlo."], key="s3_experiencia")
        st.multiselect("3. ¿Qué tipo de actividades te gustaría aprender a hacer mejor?", ["Crear o mejorar un emprendimiento propio.", "Conseguir un empleo en una empresa.", "Hacer crecer un negocio familiar o comunitario.", "Aprender a usar herramientas digitales en mi vida cotidiana.", "Diseñar soluciones para problemas en mi comunidad."], key="s3_actividades")
        st.multiselect("4. ¿Qué habilidades te gustaría desarrollar?", ["Manejar redes sociales para vender.", "Analizar datos para tomar decisiones.", "Usar hojas de cálculo, mapas o encuestas.", "Crear contenido (imágenes, videos).", "Programar o crear aplicaciones.", "Hacer campañas de marketing digital.", "Pensamiento crítico y creativo.", "Comunicación y liderazgo."], key="s3_habilidades")
        st.text_area("5. Describe en una frase qué proyecto te gustaría crear.", help="Ej: 'Conocer tecnologías para mejorar la producción sin gastar tanto'", key="s3_proyecto")
        submitted_s3 = st.form_submit_button("Guardar y Continuar")
    if submitted_s3:
        data_to_update = {"seccion3_intereses": {"sector_interes": st.session_state.s3_sector_interes, "experiencia_previa": st.session_state.s3_experiencia, "actividades_deseadas": st.session_state.s3_actividades, "habilidades_deseadas": st.session_state.s3_habilidades, "proyecto_deseado": st.session_state.s3_proyecto}}
        success, error = update_data_rest(st.session_state.firestore_doc_path, data_to_update)
        if success: st.session_state.current_section = 4; st.success("✅ ¡Sección 3 guardada!"); time.sleep(1); st.rerun()
        else: st.error("Error al actualizar los datos."); st.exception(error)

# --- SECCIÓN 4: HABILIDADES TÉCNICAS ---
elif st.session_state.current_section == 4:
    st.header("Sección 4: Tus Habilidades Técnicas")
    st.markdown("Seamos honestos sobre lo que ya sabes. Esto no es un examen, ¡es solo para saber desde dónde partimos!")
    
    # Lógica para mostrar herramientas según el interés de la sección 3
    herramientas_agritech = ["Google Maps o mapas satelitales", "Apps para clima o cultivos", "Sensores, drones o GPS agrícola", "Hojas de cálculo para siembra/ventas"]
    herramientas_fintech = ["Billeteras digitales o apps bancarias", "Calculadoras financieras", "Formularios para controlar ingresos/gastos", "Apps para vender en línea"]
    herramientas_healthtech = ["Apps de seguimiento de salud", "Formularios digitales para encuestas", "Plataformas de telemedicina", "Hojas de cálculo para pacientes"]
    herramientas_energia = ["Medidores o apps de consumo energético", "Simuladores solares o eólicos", "Apps de monitoreo ambiental", "Calculadoras de huella de carbono"]
    herramientas_generales = ["Canva", "Google Forms", "Excel", "Word", "PowerPoint", "WhatsApp Web"]
    
    lista_herramientas = herramientas_generales
    # Leemos la respuesta de la sección anterior para decidir qué herramientas mostrar
    try:
        interes = st.session_state.s3_sector_interes # Usamos la respuesta guardada
        if "Agricultura" in interes: lista_herramientas += herramientas_agritech
        elif "Dinero" in interes: lista_herramientas += herramientas_fintech
        elif "Salud" in interes: lista_herramientas += herramientas_healthtech
        elif "Energía" in interes: lista_herramientas += herramientas_energia
    except: # Si no hay respuesta aún, muestra solo las generales
        pass

    with st.form("form_s4"):
        st.slider("1. Califica tu manejo general de herramientas tecnológicas (1=Nulo, 5=Experto)", 1, 5, 2, key="s4_autoeval_tech")
        st.multiselect("2. ¿Qué herramientas digitales has utilizado antes?", lista_herramientas, key="s4_herramientas")
        st.selectbox("3. ¿Tienes alguna certificación, constancia o diploma en habilidades digitales?", ["", "Sí, reconocidas (Google, Coursera, etc.)", "Sí, de instituciones locales", "No, pero he aprendido por mi cuenta", "No, aún no he recibido capacitación"], key="s4_certs")
        st.text_area("4. Si has realizado algún proyecto con tecnología, descríbelo brevemente.", key="s4_proyecto_previo")
        submitted_s4 = st.form_submit_button("Guardar y Continuar")
    if submitted_s4:
        data_to_update = {"seccion4_habilidades_tecnicas": {"autoevaluacion_tech": st.session_state.s4_autoeval_tech, "herramientas_conocidas": st.session_state.s4_herramientas, "certificaciones": st.session_state.s4_certs, "proyecto_previo": st.session_state.s4_proyecto_previo}}
        success, error = update_data_rest(st.session_state.firestore_doc_path, data_to_update)
        if success: st.session_state.current_section = 5; st.success("✅ ¡Sección 4 guardada!"); time.sleep(1); st.rerun()
        else: st.error("Error al actualizar los datos."); st.exception(error)

# --- SECCIÓN 5: HABILIDADES BLANDAS ---
elif st.session_state.current_section == 5:
    st.header("Sección 5: Habilidades Personales")
    st.markdown("La tecnología es solo una parte. También queremos saber cómo te gusta trabajar y aprender con otros.")
    with st.form("form_s5"):
        st.selectbox("1. Cuando trabajas en equipo, ¿qué rol sueles tomar?", ["", "Prefiero observar, escuchar y seguir instrucciones.", "Me gusta compartir ideas y apoyar cuando se me solicita.", "Suelo proponer ideas, coordinar o liderar iniciativas."], key="s5_rol_equipo")
        st.slider("2. ¿Qué tan cómodo(a) te sientes comunicando tus ideas en público? (1=Incómodo, 5=Cómodo)", 1, 5, 3, key="s5_comunicacion")
        st.multiselect("3. ¿Qué habilidades personales te interesa fortalecer?", ["Comunicación efectiva", "Trabajo colaborativo", "Resolución de problemas", "Liderazgo", "Creatividad e innovación", "Organización y gestión del tiempo", "Empatía y escucha activa"], key="s5_habilidades_deseadas")
        st.selectbox("4. En los trabajos en equipo, ¿qué papel te gusta tomar?", ["", "Soy el que ayuda y sigue las indicaciones.", "Me gusta organizar y asegurar que todo salga bien.", "Me gusta liderar y tomar las decisiones importantes."], key="s5_papel_equipo")
        st.multiselect("5. ¿Cómo prefieres aprender cosas nuevas?", ["Ver cursos en internet", "Participar en foros y platicar con otros", "Hacer proyectos en grupo con la comunidad", "Usar guías fáciles que puedo descargar y leer"], key="s5_aprendizaje")
        submitted_s5 = st.form_submit_button("Finalizar Diagnóstico")
    if submitted_s5:
        data_to_update = {"seccion5_habilidades_blandas": {"rol_equipo": st.session_state.s5_rol_equipo, "comodidad_comunicando": st.session_state.s5_comunicacion, "habilidades_deseadas": st.session_state.s5_habilidades_deseadas, "papel_preferido_equipo": st.session_state.s5_papel_equipo, "preferencia_aprendizaje": st.session_state.s5_aprendizaje}, "estado": "Completado", "timestamp_final": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        success, error = update_data_rest(st.session_state.firestore_doc_path, data_to_update)
        if success: st.session_state.current_section = 6; st.success("✅ ¡Diagnóstico finalizado! Gracias por tus respuestas."); time.sleep(2); st.rerun()
        else: st.error("Error al actualizar los datos."); st.exception(error)

# --- PÁGINA FINAL ---
elif st.session_state.current_section > 5:
    st.header("🎉 ¡Has finalizado el diagnóstico! 🎉")
    st.balloons()
    st.success("¡Muchas gracias por tu tiempo! Hemos guardado tus respuestas.")
    st.markdown("En las próximas horas se te activará tu ruta de aprendizaje personalizada en la plataforma.")
    st.markdown("---")
    st.markdown("Mientras tanto, te invitamos a explorar nuestro canal de alfabetización digital:")
    st.markdown("[Visita nuestro canal aquí](https://open.spotify.com/show/5bIWnDVI2LnGTKCtdzbNDw)")
