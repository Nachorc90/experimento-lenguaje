import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import uuid
from io import BytesIO
from openpyxl import Workbook
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
¡Hola! Gracias por participar en este experimento. A continuación, te explicamos lo que vas a hacer:
A continuación van a leer una definición, tras ella verás tres palabras como opciones de respuesta con solo una palabra es la correcta.

Primero realizaremos 3 ensayos de prueba en las que vas a tener que responder con el significado de la definición.

Tras esta prueba empezaremos con los 10 ensayos en las que tienes que responder con la palabra que corresponde a la definición. 

Y para terminar realizaras otros 10 ensayos pero esta vez tendras que responder con el antonimo a la definición. 

Tener en cuenta: En cuanto le de al boton de comenzar el experimento, coemzará. Entre ensayos tiene que volver a presionar a continuar para seguir respondiendo.
Cuando haya que cambiar de condición aparecera un mensaje de aviso junto al una boton de continuar. 
""")

# -------- DICCIONARIO DE PALABRAS --------
diccionario = {
    
    "De poca altura": {"respuesta": "bajo", "antonimo": "alto"},
    "Que carece de luz": {"respuesta": "oscuro", "antonimo": "claro"},
    "Que tiene o produce calor": {"respuesta": "caliente", "antonimo": "frio"},
    "Que se mueve muy deprisa": {"respuesta": "rápido", "antonimo": "lento"},
    "Estado de grata satisfacción espiritual y física": {"respuesta": "feliz", "antonimo": "triste"},
    "Que tiene un alto precio o más alto de lo normal": {"respuesta": "caro", "antonimo": "barato"},
    "Que tiene poco tamaño": {"respuesta": "pequeño", "antonimo": "grande"},
    "Recién hecho o fabricado": {"respuesta": "nuevo", "antonimo": "viejo"},
    "Dicho de algo que es particular o personal": {"respuesta": "privado", "antonimo": "público"},
    "Que tiene longuitud": {"respuesta": "largo", "antonimo": "corto"},
    "Que no requiere gran esfuerzo, habilidad o capacidad": {"respuesta": "fácil", "antonimo": "dificil"},
    "Que no tiene mancha o suciedad": {"respuesta": "limpio", "antonimo": "sucio"},
    "Que carece de agua u otro líquido": {"respuesta": "seco", "antonimo": "mojado"},
    "Existente de hace mucho tiempo o que perdura": {"respuesta": "viejo", "antonimo": "nuevo"},
    "Que supera el tamaño": {"respuesta": "grande", "antonimo": "pequeño"},
    "Que goza de salud": {"respuesta": "sano", "antonimo": "enfermo"},
    "Que no hace ruido": {"respuesta": "silencioso", "antonimo": "ruidoso"},
    "Que impide el paso de luz": {"respuesta": "opaco", "antonimo": "transparente"},
    "Sabio, experto, instruido": {"respuesta": "inteligente", "antonimo": "tonto"},
    "Acrecentamiento o extensión de algo": {"respuesta": "aumento", "antonimo": "disminución"},
    "Que se comporta de un modo inhabitual": {"respuesta": "raro", "antonimo": "común"},
    "Libre de errores o defectos": {"respuesta": "correcto", "antonimo": "incorrecto"},
    "Comienzo de algo": {"respuesta": "inicio", "antonimo": "final"},
    "Algo ocupado hasta el límite": {"respuesta": "lleno", "antonimo": "Vacio"}
}
# -------- INICIALIZAR VARIABLES DE SESIÓN --------
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = str(random.randint(10000, 99999))
if "condicion" not in st.session_state:
    st.session_state.condicion = "Prueba"
if "resultado_guardado" not in st.session_state:
    st.session_state.resultado_guardado = False

if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.resultados = []
    st.session_state.condicion_actual =  "Prueba"
    st.session_state.transicion = False
    st.session_state.experimento_iniciado = False
    st.session_state.usadas_prueba = set()
    st.session_state.usadas_significado = set()
    st.session_state.usadas_antonimo = set()

# NUEVAS banderas para transiciones
if "transicion_significado" not in st.session_state:
    st.session_state.transicion_significado = False
if "transicion_antonimo" not in st.session_state:
    st.session_state.transicion_antonimo = False

# -------- CONFIGURACIÓN DE BASE DE DATOS --------
def inicializar_db():
    conn = sqlite3.connect('experimento.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                    usuario_id TEXT,
                    usuario TEXT,
                    ensayo INTEGER,
                    condicion TEXT,
                    definicion TEXT,
                    respuesta_usuario TEXT,
                    respuesta_correcta TEXT,
                    correcto BOOLEAN,
                    tiempo_reaccion REAL
                )''')
    conn.commit()
    conn.close()

inicializar_db()

# -------- GUARDAR RESULTADO --------
def guardar_resultado(usuario_id, usuario, ensayo, condicion, definicion, respuesta, correcta, tiempo):
    acierto = 1 if respuesta.strip().lower() == correcta.strip().lower() else 0
    try:
        with sqlite3.connect('experimento.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO resultados (usuario_id, usuario, ensayo, condicion, definicion, respuesta_usuario, respuesta_correcta, correcto, tiempo_reaccion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (usuario_id, usuario, ensayo, condicion, definicion, respuesta, correcta, acierto, tiempo))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error al guardar el resultado en la base de datos: {e}")

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
if st.session_state.ensayo <= 23:

    # Transición a Definición → Significado
    if st.session_state.ensayo == 4 and not st.session_state.transicion_significado:
        st.warning("¡Has completado la fase de Prueba! Ahora pasaremos a la siguiente fase: 10 ensayos en las que tienes que responder con la palabra que corresponde a la definición.")
        if st.button("Continuar con la segunda fase"):
            st.session_state.transicion_significado = True
            st.session_state.condicion_actual = "Definición → Significado"
            st.session_state.ensayo += 1
            st.rerun()
        else:
            st.stop()

    # Transición a Definición → Antónimo
    if st.session_state.ensayo == 14 and not st.session_state.transicion_antonimo:
        st.warning("¡Has completado la segunda fase! Ahora pasaremos a la fase final: 10 ensayos pero esta vez tendras que responder con el antonimo a la definición.")
        if st.button("Continuar con la siguiente fase"):
            st.session_state.transicion_antonimo = True
            st.session_state.condicion_actual = "Definición → Antónimo"
            st.session_state.ensayo += 1
            st.rerun()
        else:
            st.stop()

    # Generar nueva pregunta si es necesario
    if "definicion" not in st.session_state:
        usadas = {
            "Prueba": st.session_state.usadas_prueba,
            "Definición → Significado": st.session_state.usadas_significado,
            "Definición → Antónimo": st.session_state.usadas_antonimo,
        }[st.session_state.condicion_actual]

        definiciones_disponibles = [k for k in diccionario.keys() if k not in usadas]

        if not definiciones_disponibles:
            st.warning("No quedan más definiciones disponibles.")
            st.stop()

        definicion = random.choice(definiciones_disponibles)
        usadas.add(definicion)

        opciones = diccionario[definicion]
        correcta = opciones["respuesta"] if st.session_state.condicion_actual != "Definición → Antónimo" else opciones["antonimo"]

        respuestas_posibles = [correcta]
        otras_palabras = [v["respuesta"] for v in diccionario.values() if v["respuesta"] not in respuestas_posibles]

        distractores = random.sample([w for w in otras_palabras if w != correcta], 2)
        lista_opciones = [correcta] + distractores
        random.shuffle(lista_opciones)

        # Guardar en la sesión
        st.session_state.definicion = definicion
        st.session_state.correcta = correcta
        st.session_state.lista_opciones = lista_opciones
        st.session_state.t_inicio = time.time()  # Iniciar tiempo de reacción
        st.session_state.t_reaccion = None  # Reiniciar el tiempo de reacción

    # Mostrar ensayo
    st.write(f"**Ensayo {st.session_state.ensayo}/23 - {st.session_state.condicion_actual}**")
    st.write(f"**Definición:** {st.session_state.definicion}")

    # Mostrar opciones y capturar respuesta
    respuesta = st.radio("Selecciona la opción correcta:", st.session_state.lista_opciones, index=None)

    # Si el usuario responde y aún no se ha calculado el tiempo de reacción
    if respuesta and st.session_state.t_reaccion is None:
        st.session_state.t_reaccion = time.time() - st.session_state.t_inicio  # Guardar el tiempo de reacción
        st.session_state.respuesta_usuario = respuesta  # Guardar la respuesta seleccionada
        st.rerun()  # Forzar la actualización para mostrar el resultado sin que el tiempo siga contando

    # Mostrar resultado si ya hay una respuesta guardada
    if st.session_state.t_reaccion is not None:
        es_correcta = st.session_state.respuesta_usuario.strip().lower() == st.session_state.correcta.strip().lower()

        if es_correcta:
            st.success("¡Respuesta correcta! ✅")
        else:
            st.error(f"Respuesta incorrecta. La respuesta correcta era: {st.session_state.correcta} ❌")

        st.write(f"Tiempo de respuesta: {st.session_state.t_reaccion:.2f} segundos")

        # Guardar solo una vez por ensayo
        if not st.session_state.resultado_guardado:
            guardar_resultado(
                st.session_state.usuario_id,
                st.session_state.usuario,
                st.session_state.ensayo,
                st.session_state.condicion_actual,
                st.session_state.definicion,
                st.session_state.respuesta_usuario,
                st.session_state.correcta,
                st.session_state.t_reaccion
            )
            st.session_state.resultado_guardado = True

        # Botón para continuar
        if st.button("Continuar"):
            st.session_state.ensayo += 1
            st.session_state.resultado_guardado = False  # Resetear para el siguiente
            for key in ["definicion", "lista_opciones", "respuesta_usuario", "t_reaccion"]:
                st.session_state.pop(key, None)

# -------- FINALIZACIÓN DEL EXPERIMENTO --------
if st.session_state.ensayo > 23:
    st.success("🎉 **¡Has completado el experimento! Gracias por participar **")
    st.write("📊 **Descarga tus resultados**")

def descargar_resultados_excel():
    try:
        conn = sqlite3.connect('experimento.db')
        df = pd.read_sql_query(
            "SELECT * FROM resultados WHERE usuario_id = ?", 
            conn, 
            params=(st.session_state.usuario_id,)
        )
        conn.close()

        if df.empty:
            st.warning("⚠️ No hay datos disponibles para este usuario.")
            return None

        columnas_ordenadas = [
            "usuario_id", "usuario", "ensayo", "condicion", "definicion",
            "respuesta_usuario", "respuesta_correcta", "correcto", "tiempo_reaccion"
        ]
        df = df[columnas_ordenadas]

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')

            # Ajustar ancho de columnas
            workbook = writer.book
            worksheet = writer.sheets['Resultados']

            for col in worksheet.columns:
                max_length = 0
                col_letter = col[0].column_letter  # Obtener letra de la columna (A, B, C, ...)
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = (max_length + 2)  # Ancho ajustado con un poco de margen
                worksheet.column_dimensions[col_letter].width = adjusted_width

        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Error al generar el archivo Excel: {e}")
        return None

# -------- INTERFAZ DE DESCARGA --------
st.title("📊 Resultados del Experimento")
excel_data = descargar_resultados_excel()
if excel_data:
    st.download_button(
        label="📥 Descargar Resultados en Excel",
        data=excel_data,
        file_name="resultados_experimento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
