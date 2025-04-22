import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import altair as alt
from io import BytesIO

# -------- CONFIGURACIONES --------
MASTER_PASSWORD = "experimento123"

# -------- QR EN PANTALLA DE INICIO --------
app_url = "https://experimento-lenguaje-evvnuoczsrg43edwgztyrv.streamlit.app/"
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")
st.image(qr_bytes, caption="Escanea el QR para acceder al experimento", use_container_width=True)

# -------- INSTRUCCIONES --------
st.title("🧪 Experimento")
st.markdown("## Instrucciones")
st.markdown(r"""
A continuación van a leer una definición y verán dos opciones:

1. Práctica: 3 ensayos mezclados: 2 de **Significado** (definición en rojo) y 1 de **Antónimo** (definición en azul).
2. Experimental: 20 ensayos mezclados: 10 de Significado y 10 de Antónimo.

- El tiempo de reacción se mide al seleccionar.
- La opción se bloquea tras seleccionar.
- Verás tu tiempo inmediatamente.
- Tras la práctica verás un mensaje de transición.
- Descansa 30 s al finalizar.
- Al final, dos gráficos: tiempos por ensayo y tiempo medio por fase.
""")

# -------- BOTÓN DE INICIO --------
if 'started' not in st.session_state:
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.started = True
        st.rerun()
    else:
        st.stop()

# -------- DICCIONARIO --------
diccionario = {
    "De poca altura": {"respuesta": "bajo", "antonimo": "alto"},
    "Que carece de luz": {"respuesta": "oscuro", "antonimo": "claro"},
    "Que tiene o produce calor": {"respuesta": "caliente", "antonimo": "frío"},
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
    "Algo ocupado hasta el límite": {"respuesta": "lleno", "antonimo": "vacío"}
}
practice_dict = {
    "Que tiene sonido suave y delicado": {"respuesta": "suave", "antonimo": "áspero"},
    "Que es muy ligero y flota con facilidad en el agua": {"respuesta": "liviano", "antonimo": "pesado"},
    "Que está realizado con gran atención a los detalles": {"respuesta": "minucioso", "antonimo": "superficial"},
    # Añadir más ítems de práctica si se desea
}

# -------- SESIÓN --------
if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = str(random.randint(10000,99999))
if 'ensayo' not in st.session_state:
    st.session_state.ensayo = 1
    # práctica: 2 Significado + 1 Antónimo
    pract_conds = ['Significado']*2 + ['Antónimo']*1
    random.shuffle(pract_conds)
    # experimental: 10 Significado + 10 Antónimo
    exp_conds = ['Significado']*10 + ['Antónimo']*10
    random.shuffle(exp_conds)
    # secuencia completa
    st.session_state.cond_seq = pract_conds + exp_conds
    st.session_state.usadas_defs = set()
    st.session_state.respondido = False
    st.session_state.post_practica = False

# -------- INICIALIZAR BD --------
def init_db():
    conn = sqlite3.connect('experimento.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados(
        usuario_id TEXT, ensayo INTEGER, condicion TEXT,
        definicion TEXT, respuesta_usuario TEXT,
        respuesta_correcta TEXT, correcto INTEGER,
        tiempo_reaccion REAL
    )''')
    conn.commit(); conn.close()
init_db()

# -------- BUCLE --------
total_trials = len(st.session_state.cond_seq)
if st.session_state.ensayo <= total_trials:
    cond = st.session_state.cond_seq[st.session_state.ensayo - 1]
    # mensaje transición tras práctica
    if st.session_state.ensayo == len(pract_conds) + 1 and not st.session_state.post_practica:
        st.warning("¡Has completado la práctica! Ahora comienza la fase experimental de 20 ensayos.")
        if st.button("Continuar"):
            st.session_state.post_practica = True
            st.rerun()
        else:
            st.stop()
    # generar definición única
    if 'definicion' not in st.session_state:
        pool = practice_dict if st.session_state.ensayo <= len(pract_conds) else diccionario
        choices = [d for d in pool if d not in st.session_state.usadas_defs]
        defin = random.choice(choices)
        st.session_state.usadas_defs.add(defin)
        data = pool[defin]
        # respuesta correcta/distractor
        if cond == 'Significado':
            correcta = data['respuesta']; distractor = data['antonimo']
        else:
            correcta = data['antonimo']; distractor = data['respuesta']
        opts = [correcta, distractor]
        random.shuffle(opts)
        # guardar en sesión
        st.session_state.definicion = defin
        st.session_state.correcta = correcta
        st.session_state.opciones = opts
        st.session_state.t0 = time.time()
        st.session_state.respondido = False
    # color y mostrar
    color = 'red' if cond == 'Significado' else 'blue'
    st.markdown(f"<span style='color:{color}'>**Definición:** {st.session_state.definicion}</span>", unsafe_allow_html=True)
    st.write(f"**Ensayo {st.session_state.ensayo}/{total_trials} - {cond}**")
    # opciones radio
    respuesta = st.radio("Selecciona:", st.session_state.opciones,
                           index=None, disabled=st.session_state.respondido,
                           key=f"radio{st.session_state.ensayo}")
    # procesar respuesta
    if not st.session_state.respondido and respuesta is not None:
        dt = time.time() - st.session_state.t0
        st.session_state.t_reaccion = dt
        st.session_state.respondido = True
        correcto_flag = int(respuesta == st.session_state.correcta)
        with sqlite3.connect('experimento.db') as conn:
            conn.execute('INSERT INTO resultados VALUES (?,?,?,?,?,?,?,?)', (
                st.session_state.usuario_id,
                st.session_state.ensayo,
                cond,
                st.session_state.definicion,
                respuesta,
                st.session_state.correcta,
                correcto_flag,
                dt
            ))
            conn.commit()
        st.write(f"🕒 Tiempo de respuesta: {dt:.2f} segundos")
    # continuar
    if st.session_state.respondido and st.button("Continuar"):
        # limpiar estado de prueba
        for k in ['definicion', 'correcta', 'opciones', 'respondido', 't_reaccion']:
            if k in st.session_state: del st.session_state[k]
        st.session_state.ensayo += 1
        st.rerun()
else:
    # fin
    st.success("🎉 ¡Experimento completado!")
    df_all = pd.read_sql_query(
        "SELECT ensayo, condicion, tiempo_reaccion FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    # separar y trial
    df_sig = df_all[df_all['condicion']=='Significado'].copy()
    df_sig['trial'] = range(1, len(df_sig)+1)
    df_ant = df_all[df_all['condicion']=='Antónimo'].copy()
    df_ant['trial'] = range(1, len(df_ant)+1)
    plot_df = pd.concat([df_sig, df_ant])
    # gráfico ensayo
    chart1 = alt.Chart(plot_df).mark_line(point=True).encode(
        x='trial:Q', y='tiempo_reaccion:Q',
        color=alt.Color('condicion:N', scale=alt.Scale(domain=['Significado','Antónimo'], range=['red','blue']))
    ).properties(title='Tiempos de reacción por ensayo')
    st.altair_chart(chart1, use_container_width=True)
    # media
    df_mean = plot_df.groupby('condicion')['tiempo_reaccion'].mean().reset_index()
    chart2 = alt.Chart(df_mean).mark_bar().encode(
        x='condicion:N', y='tiempo_reaccion:Q',
        color=alt.Color('condicion:N', scale=alt.Scale(domain=['Significado','Antónimo'], range=['red','blue']))
    ).properties(title='Tiempo medio por fase')
    st.altair_chart(chart2, use_container_width=True)
    # descarga
    df_export = pd.read_sql_query(
        "SELECT * FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    def to_excel(df):
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
            for col in writer.sheets['Resultados'].columns:
                max_len = max(len(str(c.value)) for c in col)
                writer.sheets['Resultados'].column_dimensions[col[0].column_letter].width = max_len + 2
        buf.seek(0)
        return buf
    st.download_button("📥 Descargar resultados", data=to_excel(df_export), file_name='resultados_experimento.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
