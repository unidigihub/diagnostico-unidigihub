import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time

# --- INICIALIZACIÓN DE FIREBASE ---
def initialize_firebase():
    try:
        creds_from_secrets = st.secrets["firebase_credentials"]
        if isinstance(creds_from_secrets, str):
            creds_dict = json.loads(creds_from_secrets)
        else:
            creds_dict = dict(creds_from_secrets)
        
        cred = credentials.Certificate(creds_dict)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        st.error(f"Error CRÍTICO al inicializar Firebase: {e}")
        return False

IS_FIREBASE_INITIALIZED = initialize_firebase()
db = firestore.client() if IS_FIREBASE_INITIALIZED else None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Prueba Final UniDigiHub", layout="centered")
st.title("🔬 Prueba Final de Conexión")
st.markdown("---")

# --- SECCIÓN ÚNICA DE PRUEBA ---
st.header("Sección 1: Prueba de Escritura")
st.write("Ignora los campos. Solo presiona el botón de abajo para realizar la prueba de escritura en la base de datos.")

with st.form("form_s1"):
    # Campos de relleno, no se usarán
    st.text_input("Campo de prueba 1")
    st.text_input("Campo de prueba 2")
    submitted_s1 = st.form_submit_button("Realizar Prueba de Escritura")

if submitted_s1:
    st.info("Iniciando la prueba de escritura más simple...")
    if not IS_FIREBASE_INITIALIZED:
        st.error("La prueba no puede continuar porque la inicialización de Firebase falló. Revisa el error de arriba.")
    else:
        try:
            st.write("Intentando enviar 'hola' a la base de datos...")
            
            # La "llamada telefónica": un intento de escritura muy simple.
            db.collection("prueba_final_escritura").add({
                "mensaje": "La escritura funcionó correctamente",
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            
            # Si el código llega aquí, todo funcionó.
            st.success("✅ ¡ÉXITO! La 'llamada telefónica' a la base de datos se completó.")
            st.success("La conexión y los permisos son CORRECTOS.")
            st.balloons()
            st.info("Si ves este mensaje, el problema original podría estar relacionado con los datos del formulario. Pero ahora sabemos que la conexión funciona.")

        except Exception as e:
            # Si el código llega aquí, la escritura falló.
            st.error("❌ FALLÓ. La 'llamada telefónica' a la base de datos no se pudo completar.")
            st.error("Este es el error definitivo que nos dice el porqué:")
            st.exception(e)
