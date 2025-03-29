import streamlit as st
import random
import time
import pandas as pd
import qrcode
from io import BytesIO

# -------- CONFIGURACIONES --------
MASTER_PASSWORD = "experimento123"

st.sidebar.title("Modo Administrador")
password = st.sidebar.text_input("Ingrese la clave de administrador:", type="password")
is_master = password == MASTER_PASSWORD

# -------- DICCIONARIO DE PALABRAS --------
diccionario = {
    "Estado de ánimo positivo y de alegría": {"respuesta": "feliz", "antonimo": "triste"},
    "Que se mueve a gran velocidad": {"respuesta": "rápido", "antonimo": "lento"},
    "De gran tamaño": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que tiene mucha fuerza": {"respuesta": "fuerte", "antonimo": "débil"},
    "Que tiene mucha luz": {"respuesta": "claro", "antonimo": "oscuro"},
    "Que no tiene suciedad": {"respuesta": "limpio", "antonimo": "sucio"},
    "Que no pesa mucho": {"respuesta": "ligero", "antonimo": "pesado"},
    "Que está lleno de vida y energía": {"respuesta": "activo", "antonimo": "pasivo"},
    "Que no es duro": {"respuesta": "blando", "antonimo": "duro"},
    "Que se entiende con facilidad": {"respuesta": "simple", "antonimo": "complejo"},
    "Que tiene poca temperatura": {"respuesta": "frío", "antonimo": "caliente"},
    "Que está lleno de gente u objetos": {"respuesta": "lleno", "antonimo": "vacío"},
    "Que es nuevo o reciente": {"respuesta": "moderno", "antonimo": "antiguo"},
    "Que está en la parte superior": {"respuesta": "arriba", "antonimo": "abajo"},
    "Que es honesto y sincero": {"respuesta": "verdadero", "antonimo": "falso"},
    "Que no tiene miedo": {"respuesta": "valiente", "antonimo": "cobarde"},
    "Que no hace ruido": {"respuesta": "silencioso", "antonimo": "ruidoso"},
    "Que no está cerca": {"respuesta": "lejos", "antonimo": "cerca"},
    "Que es fácil de hacer o entender": {"respuesta": "fácil", "antonimo": "difícil"}
}

# -------- VARIABLES DE SESIÓN --------
if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.resultados = []
    st.session_state.condicion_actual = "Definición → Significado"
    st.session_state.transicion = False
    st.session_state.experimento_iniciado = False
    st.session_state.usadas = set()  # Para evitar repetir definiciones consecutivamente

# -------- BOTÓN DE INICIO --------
if not st.session_state.experimento_iniciado:
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.experimento_iniciado = True
    else:
        st.stop()

# -------- EXPERIMENTO --------
if st.session_state.ensayo <= 20:

    if st.session_state.ensayo == 11 and not st.session_state.transicion:
        st.session_state.condicion_actual = "Definición → Antónimo"
        st.session_state.transicion = True
        st.info("✅ Has completado los primeros 10 ensayos.\n\nAhora comienza la condición **Definición → Antónimo**.")
        st.stop()

    if "definicion" not in st.session_state:

        # Seleccionar una definición aleatoria que no se haya usado en el ensayo anterior
        definicion = random.choice([k for k in diccionario.keys() if k not in st.session_state.usadas])
        st.session_state.usadas.add(definicion)
        if len(st.session_state.usadas) > 5:  # Controla la repetición (ajústalo según el tamaño del diccionario)
            st.session_state.usadas.pop()

        opciones = diccionario[definicion]

        if st.session_state.condicion_actual == "Definición → Significado":
            correcta = opciones["respuesta"]
        else:
            correcta = opciones["antonimo"]

        otra_opcion = random.choice([
            v["respuesta"] if st.session_state.condicion_actual == "Definición → Significado" else v["antonimo"]
            for k, v in diccionario.items() if k != definicion
        ])

        # Crear lista de opciones y aleatorizarlas
        lista_opciones = [correcta, otra_opcion, opciones["antonimo"] if correcta == opciones["respuesta"] else opciones["respuesta"]]
        random.shuffle(lista_opciones)

        st.session_state.definicion = definicion
        st.session_state.correcta = correcta
        st.session_state.lista_opciones = lista_opciones
        st.session_state.t_inicio = time.time()

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
            st.rerun()

# -------- RESULTADOS --------
else:
    st.success("🎉 ¡Has completado los 20 ensayos!")

    df = pd.DataFrame(st.session_state.resultados)
    st.write(df)

    # Guardar CSV
    df.to_csv("resultados.csv", index=False)
    st.download_button("📥 Descargar Resultados", data=df.to_csv().encode(), file_name="resultados.csv")








