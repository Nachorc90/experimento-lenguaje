import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import hashlib
from io import BytesIO

# -------- CONFIGURACIONES --------
MASTER_PASSWORD = st.secrets["MASTER_PASSWORD"]

# -------- ÍTEMS DE PRÁCTICA (no reaparecen en el experimento) --------
practice_dict = {
    "De pocas vitaminas": {"respuesta": "hipovitaminosis", "antonimo": "hipervitaminosis"},
    "Que ruge muy fuerte": {"respuesta": "atronar", "antonimo": "susurrar"},
    "Pieza musical breve": {"respuesta": "minueto", "antonimo": "sinfonía"},
}

# -------- DICCIONARIO PRINCIPAL --------
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

# -------- CANAL DE LOGIN ANÓNIMO --------
if "usuario_id" not in st.session_state:
    st.title("🧪 Experimento Anónimo")
    user_input = st.text_input("Introduce tu identificador (anónimo)")
    if st.button("Continuar") and user_input:
        uid = hashlib.sha256(user_input.encode()).hexdigest()
        st.session_state.usuario_id = uid
        st.experimental_rerun()
    else:
        st.stop()

# -------- ORDEN DE BLOQUES CONTRABALANCEADO --------
if "block_order" not in st.session_state:
    phases = ["Definición → Significado", "Definición → Antónimo"]
    random.shuffle(phases)
    st.session_state.block_order = ["Prueba"] + phases
    st.session_state.phase_idx = 0
    st.session_state.trial_in_phase = 1
    st.session_state.resultado_guardado = False
    st.session_state.used = {phase: set() for phase in st.session_state.block_order}

phase = st.session_state.block_order[st.session_state.phase_idx]
max_trials = 3 if phase == "Prueba" else 10

# -------- INICIALIZAR BASE DE DATOS --------
def inicializar_db():
    conn = sqlite3.connect('experimento.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                    usuario_id TEXT,
                    ensayo INTEGER,
                    condicion TEXT,
                    definicion TEXT,
                    respuesta_usuario TEXT,
                    respuesta_correcta TEXT,
                    correcto INTEGER,
                    tiempo_reaccion REAL
                )''')
    conn.commit(); conn.close()

inicializar_db()

# -------- QR EN PANTALLA DE INICIO --------
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")
st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

# -------- INSTRUCCIONES --------
st.title("🧪 Experimento")
st.markdown("## Instrucciones")
st.markdown("""
1. Primero realizarás 3 ensayos de prueba con ítems piloto.
2. Luego 10 ensayos respondiendo la palabra según la definición.
3. Finalmente 10 ensayos respondiendo el antónimo de la definición.

- No verás feedback inmediato para no sesgar tus respuestas.
- Solo podrás continuar tras responder cada ensayo.
- Después de cada fase, verás un resumen y podrás descansar 30 s.
- Al final verás un gráfico con tu tiempo medio por bloque.
""")

# -------- INICIO EXPERIMENTO --------
if not st.session_state.get("started", False):
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.started = True
        st.experimental_rerun()
    else:
        st.stop()

# -------- GENERAR PREGUNTA --------
if st.session_state.trial_in_phase <= max_trials:
    if "definicion" not in st.session_state:
        pool = practice_dict if phase == "Prueba" else diccionario
        disponibles = [k for k in pool if k not in st.session_state.used[phase]]
        definicion = random.choice(disponibles)
        st.session_state.used[phase].add(definicion)
        opciones = pool[definicion]
        correcta = opciones["respuesta"] if phase != "Definición → Antónimo" else opciones["antonimo"]
        distractores = random.sample(
            [v["respuesta"] for v in diccionario.values() if v["respuesta"] != correcta],
            2
        )
        lista = [correcta] + distractores
        random.shuffle(lista)
        st.session_state.definicion = definicion
        st.session_state.correcta = correcta
        st.session_state.opciones = lista
        st.session_state.t_start = time.time()
        st.session_state.t_reaction = None

    st.markdown(f"**Fase: {phase} — Ensayo {st.session_state.trial_in_phase}/{max_trials}**")
    st.write(f"**Definición:** {st.session_state.definicion}")
    respuesta = st.radio("Selecciona una opción:", st.session_state.opciones)

    if respuesta and st.session_state.t_reaction is None:
        st.session_state.t_reaction = time.time() - st.session_state.t_start
        st.session_state.user_answer = respuesta

    if st.session_state.t_reaction is not None:
        if st.button("Continuar"):
            correcto = int(st.session_state.user_answer.lower() == st.session_state.correcta.lower())
            ensayo_global = (
                st.session_state.trial_in_phase
                + sum(3 if p == "Prueba" else 10 for p in st.session_state.block_order[:st.session_state.phase_idx])
            )
            with sqlite3.connect('experimento.db') as conn:
                conn.execute('''INSERT INTO resultados
                    (usuario_id, ensayo, condicion, definicion,
                     respuesta_usuario, respuesta_correcta, correcto, tiempo_reaccion)
                    VALUES (?,?,?,?,?,?,?,?)''',
                    (
                        st.session_state.usuario_id,
                        ensayo_global,
                        phase,
                        st.session_state.definicion,
                        st.session_state.user_answer,
                        st.session_state.correcta,
                        correcto,
                        st.session_state.t_reaction
                    )
                )
                conn.commit()
            st.session_state.trial_in_phase += 1
            for k in ["definicion", "correcta", "opciones", "t_start", "t_reaction", "user_answer"]:
                st.session_state.pop(k, None)
            st.experimental_rerun()
    else:
        st.info("Selecciona una opción para continuar...")

# -------- TRANSICIÓN ENTRE FASES --------
elif st.session_state.trial_in_phase > max_trials and st.session_state.phase_idx < len(st.session_state.block_order):
    conn = sqlite3.connect('experimento.db')
    df = pd.read_sql_query(
        "SELECT correcto, tiempo_reaccion FROM resultados WHERE usuario_id = ? AND condicion = ?",
        conn, params=(st.session_state.usuario_id, phase)
    )
    conn.close()
    if not df.empty:
        acc = df['correcto'].mean() * 100
        t_med = df['tiempo_reaccion'].mean()
        st.success(f"Fase '{phase}' completada: Precisión {acc:.1f}% · Tiempo medio {t_med:.2f}s")
    st.warning("Descansa 30 s y presiona continuar cuando estés listo.")
    if st.button("Continuar"):
        st.session_state.phase_idx += 1
        st.session_state.trial_in_phase = 1
        st.experimental_rerun()
    else:
        st.stop()

# -------- FINALIZACIÓN Y GRÁFICO --------
if st.session_state.phase_idx >= len(st.session_state.block_order):
    st.success("🎉 ¡Has completado todo el experimento!")
    conn = sqlite3.connect('experimento.db')
    df_all = pd.read_sql_query(
        "SELECT condicion, tiempo_reaccion FROM resultados WHERE usuario_id = ?",
        conn, params=(st.session_state.usuario_id,)
    )
    conn.close()
    st.markdown("## Tu tiempo medio por bloque")
    if not df_all.empty:
        chart_data = df_all.groupby('condicion')['tiempo_reaccion'].mean()
        st.line_chart(chart_data)
    else:
        st.warning("No hay datos para mostrar.")
    
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
            workbook = writer.book
            worksheet = writer.sheets['Resultados']
            for col in worksheet.columns:
                max_length = 0
                col_letter = col[0].column_letter
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                worksheet.column_dimensions[col_letter].width = max_length + 2
        output.seek(0)
        return output

    df_export = pd.read_sql_query(
        "SELECT * FROM resultados WHERE usuario_id = ?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    excel_data = to_excel(df_export)
    st.download_button(
        "📥 Descargar Resultados en Excel",
        data=excel_data,
        file_name="resultados_experimento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
