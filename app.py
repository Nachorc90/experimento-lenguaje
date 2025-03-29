import streamlit as st
import random
import time
import pandas as pd
import qrcode
from io import BytesIO
import config

MASTER_PASSWORD = "experimento123"
st.sidebar.title("Modo Administrador")
password = st.sidebar.text_input("Ingrese la clave de administrador:", type="password")
is_master = password == MASTER_PASSWORD

diccionario = {
    "Estado de ánimo positivo y de alegría": {"respuesta": "feliz", "antonimo": "triste"},
    "Que se mueve a gran velocidad": {"respuesta": "rápido", "antonimo": "lento"},
    "De gran tamaño": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que tiene mucha fuerza": {"respuesta": "fuerte", "antonimo": "débil"},
    "Que tiene mucha luz": {"respuesta": "claro", "antonimo": "oscuro"}
}

st.title("Experimento de Tiempo de Reacción")
st.write(f"**Condición actual:** {config.condicion_global}")

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

# ======== EXPERIMENTO ========
if 'ejecutando' not in st.session_state:
    st.session_state.ejecutando = False

if st.button("Iniciar Ensayo"):
    definicion, opciones = random.choice(list(diccionario.items()))
    st.session_state.definicion = definicion
    st.session_state.opciones = opciones
    st.session_state.ejecutando = True
    st.session_state.t_inicio = time.time()
    st.session_state.respuesta = None

if st.session_state.ejecutando:
    st.write(f"**Definición:** {st.session_state.definicion}")

    # Opciones
    if config.condicion_global == "Definición → Significado":
        correcta = st.session_state.opciones["respuesta"]
    else:
        correcta = st.session_state.opciones["antonimo"]

    otra_opcion = random.choice([
        v["respuesta"] if config.condicion_global == "Definición → Significado" else v["antonimo"]
        for k, v in diccionario.items() if k != st.session_state.definicion
    ])

    lista_opciones = [correcta, otra_opcion, 
                      st.session_state.opciones["antonimo"] if correcta == st.session_state.opciones["respuesta"] else st.session_state.opciones["respuesta"]]
    random.shuffle(lista_opciones)

    st.write("**Selecciona la opción correcta:**")

    col1, col2, col3 = st.columns(3)
    columnas = [col1, col2, col3]

    for i, opcion in enumerate(lista_opciones):
        if columnas[i].button(opcion.upper()):
            st.session_state.respuesta = opcion
            st.session_state.t_fin = time.time()
            st.session_state.ejecutando = False

if st.session_state.respuesta:
    tiempo_reaccion = st.session_state.t_fin - st.session_state.t_inicio
    es_correcto = st.session_state.respuesta.lower() == correcta.lower()

    st.write(f"Has seleccionado: **{st.session_state.respuesta}**")
    st.write(f"Respuesta correcta: **{correcta}**")
    st.write(f"Tiempo de reacción: {tiempo_reaccion:.3f} segundos")

    if es_correcto:
        st.success("¡Correcto!")
    else:
        st.error("Incorrecto.")

# ======== QR ========
st.subheader("Comparte el experimento")
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")
st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

