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

# Diccionario de definiciones con sus respuestas
diccionario = {
    "Estado de ánimo positivo y de alegría": {"respuesta": "feliz", "antonimo": "triste"},
    "Que se mueve a gran velocidad": {"respuesta": "rápido", "antonimo": "lento"},
    "De gran tamaño": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que tiene mucha fuerza": {"respuesta": "fuerte", "antonimo": "débil"},
    "Que tiene mucha luz": {"respuesta": "claro", "antonimo": "oscuro"}
}

# Título de la app
st.title("Experimento de Tiempo de Reacción")

# Mostrar la condición actual desde config.py
st.write(f"**Condición actual:** {config.condicion_global}")

# Solo el Master puede cambiar la condición
if is_master:
    st.success("Eres el administrador del experimento")
    
    if st.button("Cambiar Condición"):
        # Cambiar la condición entre 'Definición → Significado' y 'Definición → Antónimo'
        nueva_condicion = "Definición → Antónimo" if config.condicion_global == "Definición → Significado" else "Definición → Significado"

        # Guardar la nueva condición en config.py
        with open("config.py", "w") as f:
            f.write(f'condicion_global = "{nueva_condicion}"')

        st.success(f"Condición cambiada a: {nueva_condicion}")
        st.experimental_rerun()
else:
    st.info("Esperando instrucciones del administrador.")

# Iniciar experimento solo si no ha sido iniciado
if 'experimento_iniciado' not in st.session_state:
    st.session_state.experimento_iniciado = False

if not st.session_state.experimento_iniciado:
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.experimento_iniciado = True
else:
    # Lógica para realizar los ensayos, mostrar las definiciones, y controlar las respuestas
    if 'contador_ensayos' not in st.session_state:
        st.session_state.contador_ensayos = 0
        st.session_state.resultados = []

    # Mostrar instrucciones al principio
    st.subheader("Instrucciones:")
    st.write("1. Lee la definición proporcionada.")
    st.write("2. Elige la opción correcta.")
    st.write("3. Completa todos los ensayos para avanzar al siguiente paso.")

    if st.session_state.contador_ensayos < 10:
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
        respuesta = st.radio("Elige la opción correcta:", lista_opciones)

        if respuesta:
            # Guardar la respuesta
            tiempo_reaccion = time.time()
            es_correcto = respuesta.lower() == correcta.lower()

            st.write(f"Has seleccionado: **{respuesta}**")
            st.write(f"Respuesta correcta: **{correcta}**")

            if es_correcto:
                st.success("¡Correcto!")
            else:
                st.error("Incorrecto.")

            st.session_state.contador_ensayos += 1

            if st.session_state.contador_ensayos < 10:
                if st.button("Continuar"):
                    pass
            else:
                st.success("Has completado 10 ensayos.")
                st.write(f"**¡Ahora cambiaremos a la siguiente condición!**")
                st.session_state.contador_ensayos = 0
                st.session_state.experimento_iniciado = False
                st.experimental_rerun()

    else:
        st.info("Por favor, completa todos los ensayos antes de cambiar de condición.")
    
# Generar QR Code con la URL de la app
st.subheader("Comparte el experimento")
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"  # Cambia esto por tu URL de Streamlit cuando la subas
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")

st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)







