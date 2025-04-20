import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import hashlib
from io import BytesIO

# -------- CONFIGURACIONES --------
# Intenta obtener la contraseña maestra de secrets, si no existe, usa el valor por defecto
try:
    MASTER_PASSWORD = st.secrets["MASTER_PASSWORD"]
except Exception:
    MASTER_PASSWORD = "experimento123"

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
    "Algo ocupado hasta el límite": {"respuesta": "lleno", "antonimo": "vacío"}
}

# -------- SESIÓN ANÓNIMA --------
if "usuario_id" not in st.session_state:
    st.title("🧪 Experimento Anónimo")
    user_input = st.text_input("Introduce tu identificador (anónimo)")
    if st.button("Continuar") and user_input:
        st.session_state.usuario_id = hashlib.sha256(user_input.encode()).hexdigest()
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
    st.session_state.used = {phase: set() for phase in st.session_state.block_order}

phase = st.session_state.block_order[st.session_state.phase_idx]
max_trials = 3 if phase == "Prueba" else 10

# -------- INICIALIZAR BASE DE DATOS --------
def inicializar_db():
    conn = sqlite3.connect('experimento.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados (
        usuario_id TEXT, ensayo INTEGER, condicion TEXT,
        definicion TEXT, respuesta_usuario TEXT,
        respuesta_correcta TEXT, correcto INTEGER,
        tiempo_reaccion REAL
    )''')
    conn.commit()
    conn.close()

inicializar_db()

# -------- QR E INSTRUCCIONES --------
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
buf = BytesIO(); qr.save(buf, format="PNG")
st.image(buf, caption="Escanea el QR para acceder al experimento", use_container_width=True)
st.title("🧪 Experimento")
st.markdown("## Instrucciones")
st.markdown("""
1. Primero 3 ensayos de práctica.
2. Luego 10 ensayos respondiendo según la definición.
3. Finalmente 10 ensayos respondiendo el antónimo.

- Sin feedback inmediato.
- Solo continuar tras responder.
- Resumen y 30 s de descanso entre fases.
- Gráfico final de tiempo medio.
""")

# -------- INICIO --------
if not st.session_state.get("started", False):
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.started = True
        st.experimental_rerun()
    else:
        st.stop()

# -------- ENSAYOS --------
if st.session_state.trial_in_phase <= max_trials:
    if "definicion" not in st.session_state:
        pool = practice_dict if phase == "Prueba" else diccionario
        items = [k for k in pool if k not in st.session_state.used[phase]]
        definicion = random.choice(items)
        st.session_state.used[phase].add(definicion)
        opciones = pool[definicion]
        correcta = opciones["respuesta"] if phase != "Definición → Antónimo" else opciones["antonimo"]
        distractores = random.sample(
            [v["respuesta"] for v in diccionario.values() if v["respuesta"] != correcta], 2
        )
        lista = [correcta] + distractores; random.shuffle(lista)
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

    if st.session_state.t_reaction:
        if st.button("Continuar"):
            correcto = int(st.session_state.user_answer.lower() == st.session_state.correcta.lower())
            ensayo_global = st.session_state.trial_in_phase + sum(
                3 if p=="Prueba" else 10 for p in st.session_state.block_order[:st.session_state.phase_idx]
            )
            with sqlite3.connect('experimento.db') as conn:
                conn.execute(
                    'INSERT INTO resultados VALUES (?,?,?,?,?,?,?,?)',
                    (
                        st.session_state.usuario_id, ensayo_global, phase,
                        st.session_state.definicion, st.session_state.user_answer,
                        st.session_state.correcta, correcto, st.session_state.t_reaction
                    )
                ); conn.commit()
            st.session_state.trial_in_phase += 1
            for k in ["definicion","correcta","opciones","t_start","t_reaction","user_answer"]:
                st.session_state.pop(k, None)
            st.experimental_rerun()
    else:
        st.info("Selecciona una opción para continuar...")

# -------- TRANSICIONES --------
elif st.session_state.trial_in_phase > max_trials and st.session_state.phase_idx < len(st.session_state.block_order):
    df = pd.read_sql_query(
        "SELECT correcto, tiempo_reaccion FROM resultados WHERE usuario_id=? AND condicion=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id, phase)
    )
    if not df.empty:
        acc, t_med = df['correcto'].mean()*100, df['tiempo_reaccion'].mean()
        st.success(f"Fase '{phase}' completada: {acc:.1f}% · {t_med:.2f}s")
    st.warning("Descansa 30 s y presiona continuar cuando estés listo.")
    if st.button("Continuar"):
        st.session_state.phase_idx += 1
        st.session_state.trial_in_phase = 1
        st.experimental_rerun()
    else:
        st.stop()

# -------- FINAL Y GRÁFICO --------
if st.session_state.phase_idx >= len(st.session_state.block_order):
    st.success("🎉 ¡Experimento completado!")
    df_all = pd.read_sql_query(
        "SELECT condicion, tiempo_reaccion FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    st.markdown("## Tiempo medio por bloque")
    if not df_all.empty:
        st.line_chart(df_all.groupby('condicion')['tiempo_reaccion'].mean())
    df_export = pd.read_sql_query(
        "SELECT * FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    def to_excel(df):
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
            for col in writer.sheets['Resultados'].columns:
                max_len = max(len(str(cell.value)) for cell in col)
                col[0].column_letter and writer.sheets['Resultados'].column_dimensions[col[0].column_letter].width <= max_len+2
        buf.seek(0); return buf
    st.download_button(
        "📥 Descargar Excel", data=to_excel(df_export),
        file_name="resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
