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

st.title("🧪 Experimento de Tiempo de Reacción")
st.write(f"**Condición actual:** {config.condicion_global}")

if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.resultados = []

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

# --- EXPERIMENTO ---

if st.session_state.ensayo <= 10:
    if "definicion" not in st.session_state:
        definicion, opciones = random.choice(list(diccionario.items()))
        st.session_state.definicion = definicion

        if config.condicion_global == "Definición → Significado":
            correcta = opciones["respuesta"]
        else:
            correcta = opciones["antonimo"]

        otra_opcion = random.choice([
            v["respuesta"] if config.condicion_global == "Definición → Significado" else v["antonimo"]
            for k, v in diccionario.items() if k != definicion
        ])

        lista_opciones = [correcta, otra_opcion, opciones["antonimo"] if correcta == opciones["respuesta"] else opciones["respuesta"]]
        random.shuffle(lista_opciones)

        st.session_state.correcta = correcta
        st.session_state.lista_opciones = lista_opciones
        st.session_state.t_inicio = time.time()
        st.session_state.respuesta = None

    st.write(f"**Ensayo {st.session_state.ensayo}/10**")
    st.write(f"**Definición:** {st.session_state.definicion}")

    respuesta = st.radio(
        "Selecciona la opción correcta:",
        st.session_state.lista_opciones,
        index=None,
        key=f"respuesta_{st.session_state.ensayo}"
    )

    if respuesta:
        t_fin = time.time()
        tiempo = t_fin - st.session_state.t_inicio
        correcta = respuesta.lower() == st.session_state.correcta.lower()
        st.write(f"⏱️ Tiempo de reacción: {tiempo:.3f} segundos")
        if correcta:
            st.success("✅ ¡Correcto!")
        else:
            st.error(f"❌ Incorrecto. La respuesta era: {st.session_state.correcta}")

        # Guardar resultado
        st.session_state.resultados.append({
            "ensayo": st.session_state.ensayo,
            "definicion": st.session_state.definicion,
            "respuesta_usuario": respuesta,
            "respuesta_correcta": st.session_state.correcta,
            "correcto": correcta,
            "tiempo_reaccion": round(tiempo, 3),
            "condicion": config.condicion_global
        })

        # Botón siguiente
        if st.button("➡️ Siguiente"):
            st.session_state.ensayo += 1
            st.session_state.pop("definicion")
            st.experimental_rerun()

else:
    st.success("🎉 ¡Has completado los 10 ensayos!")
    df = pd.DataFrame(st.session_state.resultados)
    st.write(df)

    # Puedes guardar el archivo si quieres
    df.to_csv("resultados.csv", index=False)

    # QR
    st.subheader("📲 Comparte el experimento")
    app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
    qr = qrcode.make(app_url)
    qr_bytes = BytesIO()
    qr.save(qr_bytes, format="PNG")
    st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

