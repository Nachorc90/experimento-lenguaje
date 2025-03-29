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

# ---------- INSTRUCCIONES ----------
st.title("🧪 Experimento")
st.subheader("📄 Instrucciones")
st.markdown("""
A continuación Vas a ver una **definición**. Tras leerla debes elegir la opción correcta lo más rápido posible. Primero harás 10 ensayos buscando el **Significado**. Después, automáticamente pasarás a 10 ensayos buscando el **Antónimo**. Al final verás tus resultados.
""")

# ---------- VARIABLES DE SESIÓN ----------
if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.resultados = []
    st.session_state.condicion_actual = "Definición → Significado"
    st.session_state.transicion = False

# ---------- ADMINISTRADOR ----------
if is_master:
    st.sidebar.success("Eres el administrador")
    if st.sidebar.button("Reiniciar experimento"):
        for key in ["ensayo", "resultados", "condicion_actual", "transicion"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

# ---------- LÓGICA DEL EXPERIMENTO ----------
if st.session_state.ensayo <= 20:

    # Cambio de condición después de los primeros 10 ensayos
    if st.session_state.ensayo == 11 and not st.session_state.transicion:
        st.session_state.condicion_actual = "Definición → Antónimo"
        st.session_state.transicion = True
        st.info("✅ Has completado los primeros 10 ensayos.\n\nAhora comenzamos con la condición **Definición → Antónimo**.")
        st.stop()

    if "definicion" not in st.session_state:
        definicion, opciones = random.choice(list(diccionario.items()))
        st.session_state.definicion = definicion

        if st.session_state.condicion_actual == "Definición → Significado":
            correcta = opciones["respuesta"]
        else:
            correcta = opciones["antonimo"]

        otra_opcion = random.choice([
            v["respuesta"] if st.session_state.condicion_actual == "Definición → Significado" else v["antonimo"]
            for k, v in diccionario.items() if k != definicion
        ])

        lista_opciones = [correcta, otra_opcion, opciones["antonimo"] if correcta == opciones["respuesta"] else opciones["respuesta"]]
        random.shuffle(lista_opciones)

        st.session_state.correcta = correcta
        st.session_state.lista_opciones = lista_opciones
        st.session_state.t_inicio = time.time()
        st.session_state.respuesta = None

    st.write(f"**Ensayo {st.session_state.ensayo}/20**")
    st.write(f"**Condición actual:** {st.session_state.condicion_actual}")
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
            "condicion": st.session_state.condicion_actual
        })

        # Botón siguiente
        if st.button("➡️ Siguiente"):
            st.session_state.ensayo += 1
            st.session_state.pop("definicion")
            st.experimental_rerun()

# ---------- RESULTADOS ----------
else:
    st.success("🎉 ¡Has completado los 20 ensayos!")
    df = pd.DataFrame(st.session_state.resultados)
    st.write(df)

    # Guardar CSV
    df.to_csv("resultados.csv", index=False)

    # QR
    st.subheader("📲 Comparte el experimento")
    app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
    qr = qrcode.make(app_url)
    qr_bytes = BytesIO()
    qr.save(qr_bytes, format="PNG")
    st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)


st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

