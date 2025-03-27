import streamlit as st
import config  # Importamos la configuración global

# Clave secreta para el Master
MASTER_PASSWORD = "experimento123"  # Cámbiala por una más segura

# Mostrar cuadro de inicio de sesión solo si el usuario quiere ser Master
st.sidebar.title("Modo Administrador")
password = st.sidebar.text_input("Ingrese la clave de administrador:", type="password")

# Verificar si es Master
is_master = password == MASTER_PASSWORD

import streamlit as st
import random
import time
import pandas as pd
import qrcode
from io import BytesIO

# Diccionario de definiciones con sus respuestas
diccionario = {
    "Estado de ánimo positivo y de alegría": {"respuesta": "feliz", "antonimo": "triste"},
    "Que se mueve a gran velocidad": {"respuesta": "rápido", "antonimo": "lento"},
    "De gran tamaño": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que tiene mucha fuerza": {"respuesta": "fuerte", "antonimo": "débil"},
    "Que tiene mucha luz": {"respuesta": "claro", "antonimo": "oscuro"}
}

st.title("Experimento de Tiempo de Reacción")

import config  # Importamos la configuración global

st.write(f"**Condición actual:** {config.condicion_global}")

if is_master:
    st.success("Eres el administrador del experimento")
    
    if st.button("Cambiar Condición"):
        nueva_condicion = "Definición → Antónimo" if config.condicion_global == "Definición → Significado" else "Definición → Significado"

        # Guardar la nueva condición en config.py
        with open("config.py", "w") as f:
            f.write(f'condicion_global = "{nueva_condicion}"')

        st.success(f"Condición cambiada a: {nueva_condicion}")
        st.experimental_rerun()
else:
    st.info("Esperando instrucciones del administrador.")


if st.button("Iniciar Ensayo"):
    definicion, opciones = random.choice(list(diccionario.items()))
    st.write(f"**Definición:** {definicion}")
    
    t_inicio = time.time()
    respuesta = st.text_input("Escribe la respuesta y presiona Enter:")
    t_fin = time.time()
    
    if respuesta:
        tiempo_reaccion = t_fin - t_inicio
        if condicion == "Definición → Significado":
            es_correcto = respuesta.lower() == opciones["respuesta"].lower()
            palabra_correcta = opciones["respuesta"]
        else:
            es_correcto = respuesta.lower() == opciones["antonimo"].lower()
            palabra_correcta = opciones["antonimo"]
        
        st.write(f"Tiempo de reacción: {tiempo_reaccion:.3f} segundos")
        if es_correcto:
            st.success("¡Correcto!")
        else:
            st.error(f"Incorrecto. La respuesta correcta era: {palabra_correcta}")

# Generar QR Code con la URL de la app
st.subheader("Comparte el experimento")
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"  # Cambia esto por tu URL de Streamlit cuando la subas
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")

st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)
