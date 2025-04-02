import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import uuid
from io import BytesIO

# -------- CONFIGURACIONES --------
MASTER_PASSWORD = "experimento123"
usuarios_preparados = set()
usuarios_conectados = set()
experimento_iniciado = False

# -------- QR SOLO EN PANTALLA DE INICIO --------
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")
st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

# -------- INSTRUCCIONES --------
st.title("🧪 Experimento")

st.markdown("## Normas del Experimento")
st.markdown("""
1. **Instrucciones Iniciales**:
    - El experimento se dividirá en 20 ensayos en total.
    - Primero se realizarán **10 ensayos con la condición 'Definición → Significado'**.
    - Luego, se realizarán **10 ensayos con la condición 'Definición → Antónimo'**.

2. **Modo de Respuesta**:
    - En cada ensayo, se te mostrará una definición y tendrás que seleccionar la opción correcta.
    - Cada ensayo tendrá un límite de tiempo para responder, y tu tiempo de reacción será registrado.

3. **Al Finalizar**:
    - Una vez que completes los 20 ensayos, podrás ver tus resultados y descargarlos en formato CSV.

4. **Para Comenzar**:
    - Una vez que hayas leído estas instrucciones y estés listo para comenzar, haz clic en el botón **'Estoy listo'**.
""")

# -------- DICCIONARIO DE PALABRAS --------
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
    "Falta de luz o de claridad": {"respuesta": "oscuro", "antonimo": "claro"},
    "Que no tiene mucha altura": {"respuesta": "bajo", "antonimo": "alto"},
    "Que tiene una gran capacidad para aprender o entender": {"respuesta": "inteligente", "antonimo": "tonto"},
    "Que tiene mucho color": {"respuesta": "vivo", "antonimo": "apagado"},
    "Que tiene un fuerte deseo o impulso de hacer algo": {"respuesta": "ambicioso", "antonimo": "apático"},
    "Que se refiere a algo que ha sido creado o producido por un ser humano": {"respuesta": "artificial", "antonimo": "natural"},
    "Que pertenece a otro país": {"respuesta": "extranjero", "antonimo": "local"},
    "Que tiene una gran capacidad para hacer cosas": {"respuesta": "hábil", "antonimo": "torpe"},
    "Que provoca alegría o placer": {"respuesta": "divertido", "antonimo": "aburrido"},
    "Que se caracteriza por tener una forma redonda": {"respuesta": "redondo", "antonimo": "cuadrado"},
}

# -------- INICIALIZAR VARIABLES DE SESIÓN --------
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = str(uuid.uuid4())  # Genera un ID único por usuario

if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.resultados = []
    st.session_state.condicion_actual = "Definición → Significado"
    st.session_state.transicion = False
    st.session_state.experimento_iniciado = False
    st.session_state.usadas_significado = set()
    st.session_state.usadas_antonimo = set()

# -------- CONECTAR A BASE DE DATOS --------
conn = sqlite3.connect('experimento.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                usuario_id TEXT,
                ensayo INTEGER,
                definicion TEXT,
                respuesta_usuario TEXT,
                respuesta_correcta TEXT,
                correcto BOOLEAN,
                tiempo_reaccion REAL,
                condicion TEXT)''')
conn.commit()
conn.close()

# -------- FUNCIÓN PARA GUARDAR RESULTADOS --------
def guardar_resultado(usuario_id, ensayo, definicion, respuesta, correcta, tiempo):
    try:
        conn = sqlite3.connect('experimento.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resultados (usuario_id, ensayo, definicion, respuesta_usuario, respuesta_correcta, correcto, tiempo_reaccion, condicion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (usuario_id, ensayo, definicion, respuesta, correcta, respuesta.lower() == correcta.lower(), tiempo, st.session_state.condicion_actual))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error al guardar el resultado: {e}")

# -------- FORMULARIO DE INICIO DE SESIÓN --------
if st.session_state.usuario is None:
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario == "admin" and contraseña == MASTER_PASSWORD:
            st.session_state.usuario = "admin"
            st.success("¡Has iniciado sesión como administrador!")
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    st.write(f"¡Bienvenido {st.session_state.usuario}!")

# -------- BOTÓN DE INICIO DEL EXPERIMENTO --------
if not st.session_state.experimento_iniciado:
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.experimento_iniciado = True
        st.rerun()
    else:
        st.stop()

# -------- EXPERIMENTO --------
if st.session_state.ensayo <= 20:
    if st.session_state.ensayo == 11 and not st.session_state.transicion:
        # Mostrar mensaje de cambio de condición
        st.warning("¡Has completado la primera parte del experimento! Ahora pasaremos a la segunda fase: **Definición → Antónimo**, en la que se te dará una definición y tendrá que contestar con su antónimo.")
        
        # Botón para continuar con la segunda fase
        if st.button("Continuar con la segunda fase"):
            st.session_state.transicion = True  # Marcar que ya se mostró la transición
            st.session_state.usadas_significado = set()  # Reiniciar palabras usadas
            st.session_state.usadas_antonimo = set()
            st.session_state.condicion_actual = "Definición → Antónimo"
            st.rerun()  # Recargar la app para continuar
        else:
            st.stop()  # Detener ejecución hasta que el usuario haga clic

    if "definicion" not in st.session_state:
        # Determinar el conjunto de palabras usadas según la condición actual
        usadas = st.session_state.usadas_significado if st.session_state.condicion_actual == "Definición → Significado" else st.session_state.usadas_antonimo

        # Filtrar las definiciones disponibles
        definiciones_disponibles = [k for k in diccionario.keys() if k not in usadas]

        # Verificar si hay definiciones disponibles
        if not definiciones_disponibles:
            st.warning("No quedan más definiciones disponibles.")
            st.stop()

        # Seleccionar una definición al azar
        definicion = random.choice(definiciones_disponibles)
        usadas.add(definicion)

        # Obtener la respuesta correcta según la condición
        opciones = diccionario[definicion]
        correcta = opciones["respuesta"] if st.session_state.condicion_actual == "Definición → Significado" else opciones["antonimo"]

        # Generar opciones de respuesta asegurando que sean únicas
        respuestas_posibles = [opciones["respuesta"], opciones["antonimo"]]
        otras_palabras = [v["respuesta"] for k, v in diccionario.items() if v["respuesta"] not in respuestas_posibles]

        # Seleccionar dos opciones únicas que no sean la respuesta correcta
        distractores = random.sample([w for w in otras_palabras if w != correcta], 2)

        # Crear lista de opciones y mezclar
        lista_opciones = [correcta] + distractores
        random.shuffle(lista_opciones)

        # Guardar en la sesión
        st.session_state.definicion = definicion
        st.session_state.correcta = correcta
        st.session_state.lista_opciones = lista_opciones
        st.session_state.t_inicio = time.time()

    # Mostrar ensayo
    st.write(f"**Ensayo {st.session_state.ensayo}/20**")
    st.write(f"**Definición:** {st.session_state.definicion}")

    # Mostrar opciones y capturar respuesta
    respuesta = st.radio("Selecciona la opción correcta:", st.session_state.lista_opciones, index=None)

    if respuesta:
        # Calcular el tiempo de respuesta
        t_fin = time.time()
        tiempo = t_fin - st.session_state.t_inicio

        # Determinar si la respuesta es correcta o incorrecta
        es_correcta = respuesta.lower() == st.session_state.correcta.lower()

        # Mostrar el resultado de la respuesta
        if es_correcta:
            st.success("¡Respuesta correcta! ✅")
        else:
            st.error(f"Respuesta incorrecta. La respuesta correcta era: {st.session_state.correcta} ❌")

        # Mostrar el tiempo de respuesta
        st.write(f"Tiempo de respuesta: {tiempo:.2f} segundos")

        # Guardar resultado
        guardar_resultado(
            st.session_state.usuario,
            st.session_state.ensayo,
            st.session_state.definicion,
            respuesta,
            st.session_state.correcta,
            tiempo
        )

        # Mostrar botón de continuar
        if st.button("Continuar"):
            st.session_state.ensayo += 1
            st.session_state.pop("definicion")  # Eliminar la definición actual
            st.rerun()  # Recargar la app para avanzar al siguiente ensayo

else:
    st.success("🎉 ¡Has completado los 20 ensayos!")

 # -------- DESCARGAR RESULTADOS --------
    def descargar_resultados():
        conn = sqlite3.connect('experimento.db')
        df = pd.read_sql_query("SELECT * FROM resultados", conn)
        conn.close()
        return df
    
    if st.button("📥 Descargar Resultados"):
        df = descargar_resultados()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", data=csv, file_name="resultados_experimento.csv", mime="text/csv")







