import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import qrcode
import uuid
from io import BytesIO
from openpyxl import Workbook

# -------- CONFIGURACIONES --------
MASTER_PASSWORD = "experimento123"
usuarios_preparados = set()
usuarios_conectados = set()
experimento_iniciado = False

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
A continuación van a leer una definición, tras ella verás tres palabras como opciones de respuesta en la que solo una corresponde a la definición.

Primero realizaremos 3 ensayos de prueba en las que vas a tener que responder a la palabra que corresponde a la definición.

Tras esta prueba empezaremos con los 10 ensayos en las que tienes que responder con la palabra que corresponde a la definición. 

Y para terminar realizaras otros 10 ensayos pero esta vez, tendras que responder con el antonimo a la definición. 

Tener en cuenta:
- En cuanto le de al boton de comenzar el experimento, comenzará. 
- Entre ensayos tiene que volver a presionar a continuar para seguir respondiendo.
- Cuando haya que cambiar de condición aparecera un mensaje de aviso junto al una botón de continuar. 
""")

# -------- DICCIONARIO DE PALABRAS --------
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

# -------- PRÁCTICA PILOTO --------
practice_dict = {
    "Que tiene sonido suave y delicado": {"respuesta": "suave", "antonimo": "áspero"},
    "Que es muy ligero y flota con facilidad en el agua": {"respuesta": "liviano", "antonimo": "pesado"},
    "Que está realizado con gran atención a los detalles": {"respuesta": "minucioso", "antonimo": "superficial"}
}


# -------- SESIÓN STATE --------
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = str(random.randint(10000, 99999))
if "ensayo" not in st.session_state:
    st.session_state.ensayo = 1
    st.session_state.condicion_actual = "Prueba"
    st.session_state.transicion_significado = False
    st.session_state.transicion_antonimo = False
    st.session_state.experimento_iniciado = False
    st.session_state.usadas_prueba = set()
    st.session_state.usadas_significado = set()
    st.session_state.usadas_antonimo = set()
    st.session_state.respondido = False

# -------- INICIALIZAR DB --------
def inicializar_db():
    conn = sqlite3.connect('experimento.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados (
                        usuario_id TEXT, ensayo INTEGER,
                        condicion TEXT, definicion TEXT,
                        respuesta_usuario TEXT, respuesta_correcta TEXT,
                        correcto INTEGER, tiempo_reaccion REAL
                    )''')
    conn.commit()
    conn.close()
inicializar_db()

# -------- INICIO EXPERIMENTO --------
if not st.session_state.experimento_iniciado:
    if st.button("🚀 Comenzar Experimento"):
        st.session_state.experimento_iniciado = True
        st.rerun()
    else:
        st.stop()

# -------- TRANSICIONES DE FASE --------
if st.session_state.ensayo == 4 and not st.session_state.transicion_significado:
    # feedback fase Prueba
    df = pd.read_sql_query(
        "SELECT correcto, tiempo_reaccion FROM resultados WHERE usuario_id=? AND condicion='Prueba'",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    acc = df['correcto'].mean()*100 if not df.empty else 0
    t_med = df['tiempo_reaccion'].mean() if not df.empty else 0
    st.success(f"Fase 'Prueba' completada: Precisión {acc:.1f}% · Tiempo medio {t_med:.2f}s")
    st.warning("¡Ahora 10 ensayos de SIGNIFICADO!")
    if st.button("Continuar"):
        st.session_state.transicion_significado = True
        st.session_state.condicion_actual = "Significado"
        st.session_state.ensayo += 1
        st.rerun()
    else:
        st.stop()

if st.session_state.ensayo == 14 and not st.session_state.transicion_antonimo:
    # feedback fase Significado
    df = pd.read_sql_query(
        "SELECT correcto, tiempo_reaccion FROM resultados WHERE usuario_id=? AND condicion='Significado'",
        sqlite3.connect('experimento.db'), params=(st.session_state.usuario_id,)
    )
    acc = df['correcto'].mean()*100 if not df.empty else 0
    t_med = df['tiempo_reaccion'].mean() if not df.empty else 0
    st.success(f"Fase 'Significado' completada: Precisión {acc:.1f}% · Tiempo medio {t_med:.2f}s")
    st.warning("¡Ahora 10 ensayos de ANTÓNIMO!")
    if st.button("Continuar"):
        st.session_state.transicion_antonimo = True
        st.session_state.condicion_actual = "Antónimo"
        st.session_state.ensayo += 1
        st.rerun()
    else:
        st.stop()

# -------- PREGUNTA --------
if st.session_state.ensayo <= 23:
    if "definicion" not in st.session_state:
        pool = practice_dict if st.session_state.condicion_actual == "Prueba" else diccionario
        usadas = (st.session_state.usadas_prueba if st.session_state.condicion_actual == "Prueba"
                  else st.session_state.usadas_significado if st.session_state.condicion_actual == "Significado"
                  else st.session_state.usadas_antonimo)
        disponibles = [k for k in pool if k not in usadas]
        definicion = random.choice(disponibles)
        usadas.add(definicion)
        data = pool[definicion]
        correcta = data["respuesta"] if st.session_state.condicion_actual != "Antónimo" else data["antonimo"]
        distractores = random.sample(
            [v["respuesta"] for v in diccionario.values() if v["respuesta"] != correcta], 2
        )
        opciones = [correcta] + distractores
        random.shuffle(opciones)
        st.session_state.lista_opciones = opciones
        st.session_state.definicion = definicion
        st.session_state.correcta = correcta
        st.session_state.t_inicio = time.time()
        st.session_state.respondido = False

    st.write(f"**Ensayo {st.session_state.ensayo}/23 - {st.session_state.condicion_actual}**")
    st.write(f"**Definición:** {st.session_state.definicion}")

    # radio sin preselección: index=None
    respuesta = st.radio(
        "Selecciona la opción correcta:",
        st.session_state.lista_opciones,
        index=None,
        key=f"radio{st.session_state.ensayo}",
        disabled=st.session_state.respondido
    )

    # medir al seleccionar
    if not st.session_state.respondido and respuesta is not None:
        t = time.time() - st.session_state.t_inicio
        st.session_state.t_reaccion = t
        st.session_state.respuesta_usuario = respuesta
        st.session_state.respondido = True
        correcto = 1 if respuesta.lower() == st.session_state.correcta.lower() else 0
        with sqlite3.connect('experimento.db') as conn:
            conn.execute('''INSERT INTO resultados
                (usuario_id, ensayo, condicion, definicion,
                 respuesta_usuario, respuesta_correcta,
                 correcto, tiempo_reaccion)
                VALUES (?,?,?,?,?,?,?,?)''', (
                    st.session_state.usuario_id,
                    st.session_state.ensayo,
                    st.session_state.condicion_actual,
                    st.session_state.definicion,
                    respuesta,
                    st.session_state.correcta,
                    correcto,
                    t
            ))
            conn.commit()
        st.write(f"🕒 Tiempo de respuesta: {t:.2f} segundos")

    if st.session_state.respondido:
        if st.button("Continuar", key=f"cont{st.session_state.ensayo}"):
            st.session_state.ensayo += 1
            for k in ["definicion","lista_opciones","respuesta_usuario"]:
                st.session_state.pop(k, None)
            st.session_state.respondido = False
            st.rerun()
    else:
        st.info("Selecciona una opción para responder...")

# -------- FINAL Y DESCARGA --------
if st.session_state.ensayo > 23:
    st.success("🎉 ¡Has completado el experimento! Gracias por participar.")
    df = pd.read_sql_query(
        "SELECT condicion, AVG(tiempo_reaccion) as media FROM resultados WHERE usuario_id=? GROUP BY condicion",
        sqlite3.connect('experimento.db'),
        params=(st.session_state.usuario_id,)
    )
    st.line_chart(df.set_index("condicion")["media"])
    df_all = pd.read_sql_query(
        "SELECT * FROM resultados WHERE usuario_id=?",
        sqlite3.connect('experimento.db'),
        params=(st.session_state.usuario_id,)
    )
    def to_excel(df):
        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Resultados")
            for col in writer.sheets["Resultados"].columns:
                m = max(len(str(c.value)) for c in col)
                writer.sheets["Resultados"].column_dimensions[col[0].column_letter].width = m+2
        out.seek(0); return out
    st.download_button(
        "📥 Descargar Resultados en Excel",
        data=to_excel(df_all),
        file_name="resultados_experimento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
