import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import altair as alt
from io import BytesIO
from openpyxl import Workbook

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
A continuación van a leer una definición y verán tres opciones:

1. Práctica: 3 ensayos de **PRUEBA**.
2. Experimental: 20 ensayos mezclados (10 Significado, 10 Antónimo).

- El tiempo de reacción se mide al seleccionar.
- La opción se bloquea al seleccionar.
- Verás tu tiempo inmediatamente.
- Tras Prueba, verás mensaje de transición.
- Descansa 30 s al finalizar.
- Al final, dos gráficos: tiempos por ensayo y tiempo medio.
"""
)

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
    "Que está realizado con gran atención a los detalles": {"respuesta": "minucioso", "antonimo": "superficial"}
}

# -------- SESIÓN --------
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = str(random.randint(10000,99999))
if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    # secuencia: 3 Prueba + 20 mezclados
    seq = ['Prueba']*3 + ['Significado']*10 + ['Antónimo']*10
    random.shuffle(seq[3:])
    st.session_state.cond_seq = seq
    st.session_state.usadas = {'Prueba':set(),'Significado':set(),'Antónimo':set()}
    st.session_state.respondido = False
    st.session_state.post_prueba_msg = False  # para transición

# -------- DB --------
def init_db():
    conn=sqlite3.connect('experimento.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados(
        usuario_id TEXT, ensayo INT, condicion TEXT,
        definicion TEXT, respuesta_usuario TEXT,
        respuesta_correcta TEXT, correcto INT, tiempo_reaccion REAL
    )''')
    conn.commit();conn.close()
init_db()

# -------- BUCLE --------
if st.session_state.ensayo <= len(st.session_state.cond_seq):
    cond = st.session_state.cond_seq[st.session_state.ensayo-1]
    # mostrar transición tras Prueba
    if cond!='Prueba' and not st.session_state.post_prueba_msg:
        st.warning("¡Has completado la fase de PRUEBA! Ahora los 20 ensayos mezclados.")
        if st.button("Continuar"):
            st.session_state.post_prueba_msg=True
            st.rerun()
        else:
            st.stop()
    # generar ítem
    if "def" not in st.session_state:
        pool = practice_dict if cond=='Prueba' else diccionario
        used = st.session_state.usadas[cond]
        choices=[d for d in pool if d not in used]
        defin=random.choice(choices); used.add(defin)
        data=pool[defin]
        corr = data['respuesta'] if cond!='Antónimo' else data['antonimo']
        dist = random.sample([v['respuesta'] for v in diccionario.values() if v['respuesta']!=corr],2)
        opts=[corr]+dist; random.shuffle(opts)
        st.session_state.def=defin; st.session_state.corr=corr; st.session_state.opts=opts
        st.session_state.t0=time.time(); st.session_state.respondido=False
    # color y mostrar
    color = 'black'
    if cond=='Significado': color='red'
    if cond=='Antónimo': color='blue'
    st.markdown(f"<span style='color:{color}'>**Definición:** {st.session_state.def}</span>",unsafe_allow_html=True)
    st.write(f"**Ensayo {st.session_state.ensayo}/{len(st.session_state.cond_seq)} - {cond}**")
    # radio
    ans=st.radio("Selecciona:",st.session_state.opts,index=None,disabled=st.session_state.respondido)
    if not st.session_state.respondido and ans is not None:
        dt=time.time()-st.session_state.t0
        st.session_state.respondido=True
        correct=int(ans.lower()==st.session_state.corr.lower())
        with sqlite3.connect('experimento.db') as c:
            c.execute('INSERT INTO resultados VALUES(?,?,?,?,?,?,?,?)',(
                st.session_state.usuario_id,st.session_state.ensayo,
                cond,st.session_state.def,ans,st.session_state.corr,correct,dt))
            c.commit()
        st.write(f"🕒 Tiempo de respuesta: {dt:.2f} segundos")
        st.rerun()
    if st.session_state.respondido:
        if st.button("Continuar"):
            st.session_state.ensayo+=1
            for k in ['def','corr','opts','respondido']: del st.session_state[k]
            st.rerun()
else:
    st.success("🎉 ¡Experimento completado!")
    df=pd.read_sql_query(
        "SELECT ensayo,condicion,tiempo_reaccion FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'),params=(st.session_state.usuario_id,))
    # separar y trial
    sig=df[df['condicion']=='Significado'].copy(); sig['trial']=range(1,len(sig)+1)
    ant=df[df['condicion']=='Antónimo'].copy(); ant['trial']=range(1,len(ant)+1)
    plot_df=pd.concat([sig,ant])
    # gráfico por ensayo
    ch1=alt.Chart(plot_df).mark_line(point=True).encode(
        x='trial:Q', y='tiempo_reaccion:Q',
        color=alt.Color('condicion:N',scale=alt.Scale(domain=['Significado','Antónimo'],range=['red','blue']))
    ).properties(title='Tiempos por ensayo')
    st.altair_chart(ch1,use_container_width=True)
    # gráfico media
    me=plot_df.groupby('condicion')['tiempo_reaccion'].mean().reset_index()
    ch2=alt.Chart(me).mark_bar().encode(
        x='condicion:N', y='tiempo_reaccion:Q',
        color=alt.Color('condicion:N',scale=alt.Scale(domain=['Significado','Antónimo'],range=['red','blue']))
    ).properties(title='Tiempo medio por fase')
    st.altair_chart(ch2,use_container_width=True)
    # descarga
    dfall=pd.read_sql_query("SELECT * FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'),params=(st.session_state.usuario_id,))
    def to_excel(df):
        buf=BytesIO()
        with pd.ExcelWriter(buf,engine='openpyxl') as w:
            df.to_excel(w,index=False,sheet_name='Resultados')
            for col in w.sheets['Resultados'].columns:
                m=max(len(str(c.value)) for c in col)
                w.sheets['Resultados'].column_dimensions[col[0].column_letter].width=m+2
        buf.seek(0); return buf
    st.download_button("📥 Descargar resultados",data=to_excel(dfall),
        file_name='resultados.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
