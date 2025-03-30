import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
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

# ---------- Mostrar las Normas ----------
st.markdown("## Normas del Experimento")
st.markdown("""
1. **Instrucciones Iniciales**:
    - El experimento se dividirá en 20 ensayos en total.
    - Primero se realizarán **10 ensayos con la condición "Definición → Significado"**.
    - Luego, se realizarán **10 ensayos con la condición "Definición → Antónimo"**.
    
2. **Modo de Respuesta**:
    - En cada ensayo, se te mostrará una definición y tendrás que seleccionar la opción correcta.
    - Cada ensayo tendrá un límite de tiempo para responder, y tu tiempo de reacción será registrado.

3. **Al Finalizar**:
    - Una vez que completes los 20 ensayos, podrás ver tus resultados y descargarlos en formato CSV.

4. **Para Comenzar**:
    - Una vez que hayas leído estas instrucciones y estés listo para comenzar, haz clic en el botón **"Estoy listo"**.
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

# -------- INICIALIZAR VARIABLES DE SESIÓN --------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.resultados = []
    st.session_state.condicion_actual = "Definición → Significado"
    st.session_state.transicion = False
    st.session_state.experimento_iniciado = False
    st.session_state.usadas_significado = set()
    st.session_state.usadas_antonimo = set()

#--------- Conectar con la base de datos SQLite-------
conn = sqlite3.connect('experimento.db')
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                usuario_id TEXT, 
                ensayo INTEGER, 
                definicion TEXT, 
                respuesta_usuario TEXT, 
                respuesta_correcta TEXT, 
                correcto BOOLEAN, 
                tiempo_reaccion REAL,
                condicion TEXT)''')  # Se agregó la columna "condicion"

# Verificar si la columna "condicion" existe, si no, agregarla
try:
    c.execute("ALTER TABLE resultados ADD COLUMN condicion TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass  # La columna ya existe

def guardar_resultado(usuario_id, ensayo, definicion, respuesta, correcta, tiempo):
    conn = sqlite3.connect('experimento.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resultados (usuario_id, ensayo, definicion, respuesta_usuario, respuesta_correcta, correcto, tiempo_reaccion, condicion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (usuario_id, ensayo, definicion, respuesta, correcta, respuesta.lower() == correcta.lower(), tiempo, st.session_state.condicion_actual))
    conn.commit()
    conn.close()

# Generar un ID único para cada usuario
usuario_id = str(int(time.time()))  # Usar el tiempo como identificador único

# -------- INTERFAZ Y LÓGICA DEL EXPERIMENTO --------
if st.session_state.usuario == "admin":
    st.header("Resultados del Experimento")
    df = pd.read_sql_query("SELECT * FROM resultados", conn)
    st.write("**Resultados de todos los usuarios**:")
    st.write(df)
    st.download_button("📥 Descargar Resultados", data=df.to_csv().encode(), file_name="resultados.csv")
else:
    st.write("¡El experimento ha comenzado! El administrador verá los resultados.")

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

# -# -------- EXPERIMENTO --------
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
        
        # Guardar el resultado del ensayo en la base de datos
        guardar_resultado(usuario_id, st.session_state.ensayo, st.session_state.definicion, respuesta, st.session_state.correcta, correcta, tiempo)

        # Botón siguiente
        if st.button("➡️ Siguiente"):
            st.session_state.ensayo += 1
            st.session_state.pop("definicion")
            st.rerun()
else:
    st.success("🎉 ¡Has completado los 20 ensayos!")
    st.write(f"Los resultados para el usuario {usuario_id} han sido guardados.")

   # Función para consultar los resultados desde la base de datos
def obtener_resultados():
    conn = sqlite3.connect('experimento.db')
    df = pd.read_sql_query("SELECT * FROM resultados", conn)
    conn.close()
    return df

# Muestra los resultados si el administrador o investigador está viendo la aplicación
if st.session_state.usuario == "admin":  # Verifica si es el administrador
    st.header("Resultados del Experimento")
    
    # Obtener los resultados de la base de datos
    df = obtener_resultados()

    # Mostrar los resultados en una tabla
    st.write("**Resultados de todos los usuarios**:")
    st.write(df)

    # Opción para descargar los resultados como un archivo CSV
    st.download_button("📥 Descargar Resultados", data=df.to_csv().encode(), file_name="resultados.csv")

else:
    st.write("¡El experimento ha comenzado! El administrador verá los resultados.")




