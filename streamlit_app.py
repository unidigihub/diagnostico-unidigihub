
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- Configuración Firebase (reemplaza con tus datos) ---
firebase_config = {
    "apiKey": "AIzaSyAySYB9lHdc1TkcwSDV_ul53QV1AHK7H9c",
    "authDomain": "diagnostico-unidigihub.firebaseapp.com",
    "projectId": "diagnostico-unidigihub",
    "storageBucket": "diagnostico-unidigihub.firebasestorage.app",
    "messagingSenderId": "1070638609739",
    "appId": "1:1070638609739:web:99c1c2827f3980e2c664ce",
    "measurementId": "G-WD5QQZMKWN"
}

# Inicializar Firebase Admin
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': firebase_config["projectId"],
    })
db = firestore.client()

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Diagnóstico UniDigiHub", layout="centered")
st.image("logo_unidigihub.png", width=200)

st.title("Sección 1 – Datos demográficos")
st.write("Gracias por participar. Por favor completa la información:")

with st.form("form_seccion1"):
    pais = st.selectbox("¿En qué país resides?", ["México", "Guatemala", "Colombia", "Perú", "Chile"])
    edad = st.number_input("Edad", min_value=12, max_value=100, step=1)
    comunidad = st.text_input("Comunidad / ciudad")
    acceso_internet = st.selectbox("¿Tienes acceso estable a internet?", ["Sí", "No", "A veces"])
    dispositivo = st.selectbox("¿Qué dispositivo usas principalmente?", ["Celular", "Computadora", "Tablet"])
    cultural = st.text_input("Identidad cultural (si aplica)")
    enviado = st.form_submit_button("Enviar sección 1")

if enviado:
    doc = {
        "pais": pais,
        "edad": edad,
        "comunidad": comunidad,
        "internet": acceso_internet,
        "dispositivo": dispositivo,
        "cultural": cultural,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("diagnostico_seccion1").add(doc)
    st.success("¡Gracias! Sección 1 enviada correctamente.")

st.write("Este formulario automáticamente guardará tus respuestas en Firestore.")
