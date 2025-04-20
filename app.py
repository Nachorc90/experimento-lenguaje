import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import hashlib
from io import BytesIO

# -------- CONFIGURACIONES --------
try:
    MASTER_PASSWORD = st.secrets["MASTER_PASSWORD"]
except KeyError:
    MASTER_PASSWORD = "experimento123"

# -------- ÍTEMS DE PRÁCTICA --------
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
    "Que tiene longitud": {"respuesta": "largo", "antonimo": "corto"},
    "Que no requiere gran esfuerzo, habilidad o capacidad": {"respuesta": "fácil", "antonimo": "difícil"},
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
    "Algo ocupado hasta el límite": {"respuesta": "lleno", "antonimo": "vacío"},
}

# -------- INICIALIZAR BASE DE DATOS --------
def inicializar_db():
    conn = sqlite3.connect('experimento.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados (
        usuario_id TEXT,
        ensayo INTEGER,
        fase TEXT,
        definicion TEXT,
        respuesta_usuario TEXT,
        respuesta_correcta TEXT,
        correcto INTEGER,
        tiempo_reaccion REAL
    )''')
    conn.commit()
    conn.close()

inicializar_db()

# -------- LOGIN ANÓNIMO --------
if 'usuario_id' not in st.session_state:
    st.title("🧪 Experimento Anónimo")
    uid = st.text_input("Introduce tu identificador (anónimo)")
    if st.button("Continuar") and uid:
        st.session_state.usuario_id = hashlib.sha256(uid.encode()).hexdigest()
        st.stop()
    else:
        st.stop()

# -------- CONFIGURAR FASES --------
fases = ['Prueba', 'Significado', 'Antónimo']
if 'block_order' not in st.session_state:
    order = ['Prueba'] + random.sample(fases[1:], 2)
    st.session_state.block_order = order
    st.session_state.phase_idx = 0
    st.session_state.trial = 1
    st.session_state.answered = False
    st.session_state.used = {f: set() for f in order}

fase = st.session_state.block_order[st.session_state.phase_idx]
max_trials = 3 if fase == 'Prueba' else 10

# -------- QR E INSTRUCCIONES --------
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
buf = BytesIO(); qr.save(buf, format='PNG')
st.image(buf, caption='Escanea el QR para acceder al experimento', use_container_width=True)

st.title("🧪 Experimento")
st.markdown("## Instrucciones")
st.markdown("""
1. Primero 3 ensayos de práctica (Prueba).
2. Luego 10 ensayos respondiendo la palabra según la definición (Significado).
3. Finalmente 10 ensayos respondiendo el antónimo de la definición (Antónimo).

- No verás feedback de corrección hasta el final de cada fase.
- Para cada ensayo: selecciona una opción y pulsa **Continuar**.
- Tras pulsar, verás tu tiempo de respuesta.
- Luego pulsa **Siguiente ensayo** para continuar.
- Descansa 30 s al finalizar cada fase.
- Al terminar, obtendrás un gráfico con tu tiempo medio por fase.
""")

# -------- CICLO DE ENSAYOS --------
if st.session_state.trial <= max_trials:
    # Preparar ítem
    if 'definicion' not in st.session_state:
        pool = practice_dict if fase == 'Prueba' else diccionario
        restantes = [d for d in pool if d not in st.session_state.used[fase]]
        definicion = random.choice(restantes)
        st.session_state.used[fase].add(definicion)
        opciones = pool[definicion]
        correcta = opciones['respuesta'] if fase != 'Antónimo' else opciones['antonimo']
        distractores = random.sample(
            [v['respuesta'] for v in diccionario.values() if v['respuesta'] != correcta], 2
        )
        lista = [''] + [correcta] + distractores
        random.shuffle(lista[1:])  # shuffle only actual options
        st.session_state.definicion = definicion
        st.session_state.correcta = correcta
        st.session_state.opciones = lista
        st.session_state.t_start = time.time()
        st.session_state.answered = False

    # Mostrar pregunta
    st.markdown(f"**Fase: {fase} — Ensayo {st.session_state.trial}/{max_trials}**")
    st.write(f"**Definición:** {st.session_state.definicion}")
    respuesta = st.radio("Selecciona una opción:", st.session_state.opciones, index=0)

    # Pulsar Continuar para medir tiempo
    if not st.session_state.answered:
        if respuesta:
            if st.button("Continuar"):
                t_reaction = time.time() - st.session_state.t_start
                st.session_state.t_reaction = t_reaction
                st.session_state.user_answer = respuesta
                # Guardar en BD
                correcto = int(respuesta.lower() == st.session_state.correcta.lower())
                ensayo_global = st.session_state.trial + sum(
                    3 if f=='Prueba' else 10 for f in st.session_state.block_order[:st.session_state.phase_idx]
                )
                with sqlite3.connect('experimento.db') as conn:
                    conn.execute('''INSERT INTO resultados VALUES (?,?,?,?,?,?,?,?)''', (
                        st.session_state.usuario_id,
                        ensayo_global,
                        fase,
                        st.session_state.definicion,
                        respuesta,
                        st.session_state.correcta,
                        correcto,
                        t_reaction
                    ))
                    conn.commit()
                st.session_state.answered = True
                st.stop()
        else:
            st.info("Selecciona una opción para continuar...")

    # Mostrar tiempo y botón siguiente
    else:
        st.write(f"Tiempo de respuesta: {st.session_state.t_reaction:.2f} segundos")
        if st.button("Siguiente ensayo"):
            st.session_state.trial += 1
            for k in ['definicion','correcta','opciones','t_start','t_reaction','user_answer']:
                st.session_state.pop(k, None)
            st.stop()

# -------- TRANSICIÓN DE FASE --------
elif st.session_state.trial > max_trials and st.session_state.phase_idx < len(st.session_state.block_order)-1:
    df = pd.read_sql_query(
        "SELECT correcto, tiempo_reaccion FROM resultados WHERE usuario_id=? AND fase=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id, fase)
    )
    acc = df['correcto'].mean()*100 if not df.empty else 0
    t_med = df['tiempo_reaccion'].mean() if not df.empty else 0
    st.success(f"Fase '{fase}' completada: Precisión {acc:.1f}% · Tiempo medio {t_med:.2f}s")
    st.warning("Descansa 30 s y presiona continuar cuando estés listo.")
    if st.button("Continuar"):
        st.session_state.phase_idx += 1
        st.session_state.trial = 1
        st.stop()
    else:
        st.stop()

# -------- FINALIZACIÓN Y GRÁFICO --------
if st.session_state.trial > max_trials and st.session_state.phase_idx == len(st.session_state.block_order)-1:
    # última fase completada
    df = pd.read_sql_query(
        "SELECT correcto, tiempo_reaccion FROM resultados WHERE usuario_id=? AND fase=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id, fase)
    )
    acc = df['correcto'].mean()*100 if not df.empty else 0
    t_med = df['tiempo_reaccion'].mean() if not df.empty else 0
    st.success(f"Fase '{fase}' completada: Precisión {acc:.1f}% · Tiempo medio {t_med:.2f}s")
    st.success("🎉 ¡Experimento completado!")
    df_all = pd.read_sql_query(
        "SELECT fase, tiempo_reaccion FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    st.markdown("## Tiempo medio por fase")
    if not df_all.empty:
        st.line_chart(df_all.groupby('fase')['tiempo_reaccion'].mean())
    # descarga Excel
    def to_excel(df):
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
            ws = writer.sheets['Resultados']
            for col in ws.columns:
                max_len = max(len(str(cell.value)) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = max_len + 2
        buf.seek(0)
        return buf
    df_export = pd.read_sql_query(
        "SELECT * FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    excel_data = to_excel(df_export)
    st.download_button(
        "📥 Descargar Resultados en Excel",
        data=excel_data,
        file_name="resultados_experimento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
