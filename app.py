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

# -------- ESTADO COMPARTIDO --------
@st.cache_resource
def get_ready_users():
    return set()

ready_users = get_ready_users()

@st.cache_resource
def get_master():
    return {"name": None, "started": False}

master = get_master()

# -------- IDENTIFICACIÓN --------
st.sidebar.title("Bienvenido al Experimento")
user_name = st.sidebar.text_input("Ingresa tu nombre para unirte:")

if not user_name:
    st.warning("Por favor, ingresa tu nombre para continuar.")
    st.stop()

# -------- DEFINIR EL MASTER --------
if master["name"] is None:
    master["name"] = user_name  # El primer usuario en ingresar será el Master

is_master = user_name == master["name"]

# -------- PARTICIPANTES --------
if not is_master:
    if user_name not in ready_users:
        if st.button("✅ Estoy listo para comenzar"):
            ready_users.add(user_name)
            st.rerun()
    st.info(f"Esperando que **{master['name']}** inicie el experimento...")

# -------- ADMINISTRADOR --------
else:
    st.sidebar.success(f"🎩 Eres el administrador ({user_name})")
    st.sidebar.write(f"🔵 Participantes listos: {len(ready_users)}")
    
    if st.sidebar.button("🚀 Iniciar experimento"):
        master["started"] = True
        st.rerun()

# -------- INICIO DEL EXPERIMENTO --------
if not master["started"]:
    st.warning("Esperando a que el administrador inicie el experimento...")
    st.stop()

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
    st.session_state.usadas_significado = set()
    st.session_state.usadas_antonimo = set()

# -------- ADMINISTRADOR --------
if is_master:
    st.sidebar.success("Eres el administrador")
    if st.sidebar.button("Reiniciar experimento"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -------- EXPERIMENTO --------
if st.session_state.ensayo <= 20:
    if "definicion" not in st.session_state:
        definicion = "Ejemplo de definición"
        st.session_state.definicion = definicion
        st.session_state.correcta = "Respuesta correcta"
        st.session_state.lista_opciones = ["Opción 1", "Opción 2", "Respuesta correcta"]
        random.shuffle(st.session_state.lista_opciones)
        st.session_state.t_inicio = time.time()

    st.write(f"**Ensayo {st.session_state.ensayo}/20**")
    st.write(f"**Definición:** {st.session_state.definicion}")

    respuesta = st.radio("Selecciona la opción correcta:", st.session_state.lista_opciones, index=None)
    
    if respuesta:
        t_fin = time.time()
        tiempo = t_fin - st.session_state.t_inicio
        correcta = respuesta.lower() == st.session_state.correcta.lower()
        st.write(f"⏱️ Tiempo de reacción: {tiempo:.3f} segundos")
        st.success("✅ ¡Correcto!") if correcta else st.error(f"❌ Incorrecto. La respuesta era: {st.session_state.correcta}")
        
        st.session_state.resultados.append({
            "ensayo": st.session_state.ensayo,
            "definicion": st.session_state.definicion,
            "respuesta_usuario": respuesta,
            "respuesta_correcta": st.session_state.correcta,
            "correcto": correcta,
            "tiempo_reaccion": round(tiempo, 3)
        })
        
        if st.button("➡️ Siguiente"):
            st.session_state.ensayo += 1
            st.session_state.pop("definicion")
            st.rerun()

# -------- RESULTADOS --------
else:
    st.success("🎉 ¡Has completado los 20 ensayos!")
    df = pd.DataFrame(st.session_state.resultados)
    st.write(df)
    df.to_csv("resultados.csv", index=False)
    st.download_button("📥 Descargar Resultados", data=df.to_csv().encode(), file_name="resultados.csv")









