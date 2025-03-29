import streamlit as st
import random
import time
import pandas as pd
import qrcode
from io import BytesIO
import config  # Configuración global

# =========================
# CONFIGURACIÓN MASTER
# =========================
MASTER_PASSWORD = "experimento123"

# Sidebar para el administrador
st.sidebar.title("Modo Administrador")
password = st.sidebar.text_input("Ingrese la clave de administrador:", type="password")
is_master = password == MASTER_PASSWORD

# =========================
# DICCIONARIO
# =========================
diccionario = {
    "Estado de ánimo positivo y de alegría": {"respuesta": "feliz", "antonimo": "triste"},
    "Que se mueve a gran velocidad": {"respuesta": "rápido", "antonimo": "lento"},
    "De gran tamaño": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que tiene mucha fuerza": {"respuesta": "fuerte", "antonimo": "débil"},
    "Que tiene mucha luz": {"respuesta": "claro", "antonimo": "oscuro"}
}

# =========================
# INTERFAZ
# =========================
st.title("Experimento de Tiempo de Reacción")
st.write(f"**Condición actual:** {config.condicion_global}")

# SOLO MASTER PUEDE CAMBIAR LA CONDICIÓN
if is_master:
    st.success("Eres el administrador del experimento")

    if st.button("Cambiar Condición"):
        nueva_condicion = "Definición → Antónimo" if config.condicion_global == "Definición → Significado" else "Definición → Significado"
        with open("config.py", "w") as f:
            f.write(f'condicion_global = "{nueva_condicion}"\n')
        st.success(f"Condición cambiada a: {nueva_condicion}")
        st.experimental_rerun()
else:
    st.info("Esperando instrucciones del administrador.")

# =========================
# EXPERIMENTO
# =========================
if st.button("Iniciar Ensayo"):
    definicion, opciones = random.choice(list(diccionario.items()))
    st.write(f"**Definición:** {definicion}")

    # Generar opciones
    if config.condicion_global == "Definición → Significado":
        correcta = opciones["respuesta"]
    else:
        correcta = opciones["antonimo"]

    # Otra opción aleatoria
    otra_opcion = random.choice([
        v["respuesta"] if config.condicion_global == "Definición → Significado" else v["antonimo"]
        for k, v in diccionario.items() if k != definicion
    ])

    lista_opciones = [correcta, otra_opcion, opciones["antonimo"] if correcta == opciones["respuesta"] else opciones["respuesta"]]
    random.shuffle(lista_opciones)

    # Mostrar opciones
    t_inicio = time.time()
    respuesta = st.radio("Elige la opción correcta:", lista_opciones)

    if respuesta:
        t_fin = time.time()
        tiempo_reaccion = t_fin - t_inicio
        es_correcto = respuesta.lower() == correcta.lower()

        st.write(f"Has seleccionado: **{respuesta}**")
        st.write(f"Respuesta correcta: **{correcta}**")
        st.write(f"Tiempo de reacción: {tiempo_reaccion:.3f} segundos")

        if es_correcto:
            st.success("¡Correcto!")
        else:
            st.error("Incorrecto.")

# =========================
# QR CODE
# =========================
st.subheader("Comparte el experimento")
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")
st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

