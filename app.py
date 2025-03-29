import streamlit as st
import random
import time
import pandas as pd
import qrcode
from io import BytesIO
import config  # Importamos la configuración global

# Clave secreta para el Master
MASTER_PASSWORD = "experimento123"  # Cámbiala por una más segura

# Mostrar cuadro de inicio de sesión solo si el usuario quiere ser Master
st.sidebar.title("Modo Administrador")
password = st.sidebar.text_input("Ingrese la clave de administrador:", type="password")

# Verificar si es Master
is_master = password == MASTER_PASSWORD

# Diccionario de definiciones
diccionario = {
    "Estado de ánimo positivo y de alegría": {"respuesta": "feliz", "antonimo": "triste"},
    "Que se mueve a gran velocidad": {"respuesta": "rápido", "antonimo": "lento"},
    "De gran tamaño": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que tiene mucha fuerza": {"respuesta": "fuerte", "antonimo": "débil"},
    "Que tiene mucha luz": {"respuesta": "claro", "antonimo": "oscuro"}
}

# Título
st.title("🧪 Experimento de Tiempo de Reacción")

# Mostrar condición actual
st.write(f"**Condición actual:** {config.condicion_global}")

# Configuración Master
if is_master:
    st.success("Eres el administrador del experimento")
    
    if st.button("Cambiar Condición"):
        nueva_condicion = "Definición → Antónimo" if config.condicion_global == "Definición → Significado" else "Definición → Significado"

        with open("config.py", "w") as f:
            f.write(f'condicion_global = "{nueva_condicion}"')

        st.success(f"Condición cambiada a: {nueva_condicion}")
        st.experimental_rerun()
else:
    st.info("Esperando instrucciones del administrador.")

# Iniciar ensayo
if st.button("Iniciar Ensayo"):
    definicion, opciones = random.choice(list(diccionario.items()))
    st.session_state.definicion = definicion

    # Elegir la respuesta correcta según condición
    if config.condicion_global == "Definición → Significado":
        correcta = opciones["respuesta"]
    else:
        correcta = opciones["antonimo"]

    # Crear lista de opciones
    otra_opcion = random.choice([
        v["respuesta"] if config.condicion_global == "Definición → Significado" else v["antonimo"]
        for k, v in diccionario.items() if k != definicion
    ])
    lista_opciones = [correcta, otra_opcion, opciones["antonimo"] if correcta == opciones["respuesta"] else opciones["respuesta"]]
    random.shuffle(lista_opciones)

    st.session_state.lista_opciones = lista_opciones
    st.session_state.correcta = correcta
    st.session_state.t_inicio = time.time()

# Mostrar pregunta si ya se inició
if "definicion" in st.session_state:
    st.write(f"**Definición:** {st.session_state.definicion}")

    respuesta = st.radio(
        "Selecciona la opción correcta:",
        st.session_state.lista_opciones,
        index=None,  # Para que no haya ninguna marcada
        key="respuesta"
    )

    if respuesta:
        st.session_state.t_fin = time.time()

# Mostrar resultado
if "respuesta" in st.session_state and st.session_state.respuesta:
    tiempo_reaccion = st.session_state.t_fin - st.session_state.t_inicio
    es_correcto = st.session_state.respuesta.lower() == st.session_state.correcta.lower()

    st.write(f"Has seleccionado: **{st.session_state.respuesta}**")
    st.write(f"Respuesta correcta: **{st.session_state.correcta}**")
    st.write(f"⏱️ Tiempo de reacción: {tiempo_reaccion:.3f} segundos")

    if es_correcto:
        st.success("¡Correcto!")
    else:
        st.error("Incorrecto.")

# QR
st.subheader("📲 Comparte el experimento")
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"  # Cambia esto por tu URL
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")

st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

