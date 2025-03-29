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



# -------- INSTRUCCIONES --------
st.title("🧪 Experimento de Tiempo de Reacción")

st.subheader("📄 Instrucciones")
st.markdown("""
1. Vas a ver una **definición**.
2. Deberás elegir la opción correcta lo más rápido posible.
3. Harás 10 ensayos buscando el **Significado**.
4. Después, harás 10 ensayos buscando el **Antónimo**.
5. Al final podrás ver tus resultados.
""")

# -------- DICCIONARIO DE PALABRAS (SIN REPETIR LA PALABRA EN SU DEFINICIÓN) --------
diccionario = {
    "Estado de ánimo positivo y de alegría": {"respuesta": "feliz", "antonimo": "triste"},
    "Movimiento a gran velocidad": {"respuesta": "rápido", "antonimo": "lento"},
    "De dimensiones superiores a lo común": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que posee una notable resistencia o vigor": {"respuesta": "fuerte", "antonimo": "débil"},
    "Con una gran cantidad de iluminación": {"respuesta": "claro", "antonimo": "oscuro"},
    "Sin suciedad ni impurezas": {"respuesta": "limpio", "antonimo": "sucio"},
    "De peso reducido": {"respuesta": "ligero", "antonimo": "pesado"},
    "Lleno de energía y dinamismo": {"respuesta": "activo", "antonimo": "pasivo"},
    "De textura suave y fácil de comprimir": {"respuesta": "blando", "antonimo": "duro"},
    "Que se puede comprender sin dificultad": {"respuesta": "simple", "antonimo": "complejo"},
    "Con una temperatura reducida": {"respuesta": "frío", "antonimo": "caliente"},
    "Con una gran cantidad de objetos o personas": {"respuesta": "lleno", "antonimo": "vacío"},
    "Que pertenece a tiempos recientes": {"respuesta": "moderno", "antonimo": "antiguo"},
    "Ubicado en la parte superior de algo": {"respuesta": "arriba", "antonimo": "abajo"},
    "Caracterizado por decir la verdad": {"respuesta": "verdadero", "antonimo": "falso"},
    "Con ausencia de miedo": {"respuesta": "valiente", "antonimo": "cobarde"},
    "Sin emisión de sonidos": {"respuesta": "silencioso", "antonimo": "ruidoso"},
    "Situado a gran distancia": {"respuesta": "lejos", "antonimo": "cerca"},
    "Que no requiere mucho esfuerzo para entenderse": {"respuesta": "fácil", "antonimo": "difícil"}
}

# -------- QR SOLO EN PANTALLA DE INICIO --------
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")
st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

# -------- VARIABLES DE SESIÓN --------
if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.resultados = []
    st.session_state.condicion_actual = "Definición → Significado"
    st.session_state.transicion = False
    st.session_state.experimento_iniciado = False
    st.session_state.usadas_significado = set()  # Inicializa el conjunto para las palabras usadas
    st.session_state.usadas_antonimo = set()  # Inicializa el conjunto para las palabras usadas en la segunda parte


# -------- ADMINISTRADOR --------
if is_master:
    st.sidebar.success("Eres el administrador")
    if st.sidebar.button("Reiniciar experimento"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -------- BOTÓN DE INICIO --------
if not st.session_state.experimento_iniciado:
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.experimento_iniciado = True
    else:
        st.stop()

# -------- TRANSICIÓN ENTRE CONDICIONES --------
if st.session_state.ensayo == 11 and not st.session_state.transicion:
    st.session_state.condicion_actual = "Definición → Antónimo"
    st.session_state.transicion = True
    st.info("✅ Has completado los primeros 10 ensayos.\n\nAhora comienza la condición **Definición → Antónimo**.")
    if st.button("➡️ Continuar"):
        st.rerun()
    st.stop()

# -------- EXPERIMENTO --------
if st.session_state.ensayo <= 20:

    if "definicion" not in st.session_state:

        # Determinar el conjunto de palabras usadas según la condición actual
        if st.session_state.condicion_actual == "Definición → Significado":
            usadas = st.session_state.usadas_significado
        else:
            usadas = st.session_state.usadas_antonimo

        # Seleccionar una definición que no se haya usado en esta condición
        definicion = random.choice([k for k in diccionario.keys() if k not in usadas])
        usadas.add(definicion)

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









