import streamlit as st
from groq import Groq
from fpdf import FPDF
import base64
from datetime import datetime
import difflib
import os

# =========================================================
# CONFIG API
# =========================================================
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = "TU_GROQ_KEY_ACA"

client = Groq(api_key=api_key)

# =========================================================
# CONFIG APP
# =========================================================
st.set_page_config(
    page_title="QA_Helper",
    page_icon="✅",
    layout="wide"
)

# =========================================================
# CLEAN TEXT
# =========================================================
def clean_text(text):
    if not text:
        return ""

    text = str(text)

    replacements = {
        '●': '*', '•': '*', '—': '-', '–': '-',
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '…': '...', '\u2013': '-', '\u2014': '-'
    }

    for c, r in replacements.items():
        text = text.replace(c, r)

    return text.encode("latin-1", "ignore").decode("latin-1")


# =========================================================
# PDF CLASS
# =========================================================
class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")


# =========================================================
# PDF DPR GENERATION
# =========================================================
def generar_pdf(datos):

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---------------- PORTADA ----------------
    pdf.add_page()

    logo_path = "claro_logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, 10, 8, 25)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(
        0,
        10,
        clean_text("Documentación Prueba de Rendimiento Claro Argentina (DPR)"),
        0,
        1,
        "C"
    )

    pdf.ln(5)

    # ---------------- HISTORIAL ----------------
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "1. Historial", 1, 1)

    pdf.set_font("Arial", "", 8)

    pdf.cell(35, 7, "Fecha", 1)
    pdf.cell(25, 7, "Versión", 1)
    pdf.cell(75, 7, "Descripción", 1)
    pdf.cell(55, 7, "Autor", 1, 1)

    pdf.cell(35, 7, clean_text(datos["h_fecha"]), 1)
    pdf.cell(25, 7, clean_text(datos["h_version"]), 1)
    pdf.cell(75, 7, clean_text(datos["h_desc"]), 1)
    pdf.cell(55, 7, clean_text(datos["h_autor"]), 1, 1)

    pdf.ln(5)

    # ---------------- DESCRIPCIÓN ----------------
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, u"2. Descripción", 1, 1)

    pdf.set_font("Arial", "", 8)
    
    if datos["descripcion_list"]:
        texto_desc = "\n".join([f"[X] {item}" for item in datos["descripcion_list"]])
    else:
        texto_desc = "No se seleccionaron tipos de prueba."

    lines_desc = pdf.multi_cell(0, 5, clean_text(texto_desc), split_only=True)
    alt_desc = max(len(lines_desc) * 5, 7)

    pdf.multi_cell(0, 5, clean_text(texto_desc), 1)

    pdf.ln(5)

    # ---------------- OBJETIVO ----------------
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "3. Objetivo", 1, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, clean_text(datos["objetivo"]), 1)

    pdf.ln(5)

    # ---------------- ALCANCE ----------------
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "4. Alcance", 1, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, clean_text(datos["alcance"]), 1)

    pdf.ln(5)

    # ---------------- SWAGGERS ----------------
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "5. Swaggers", 1, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, clean_text(datos["swaggers"]), 1)

    pdf.ln(5)

    # ---------------- ENDPOINTS ----------------
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "6. Endpoints", 1, 1)

    pdf.set_font("Arial", "", 8)

    for ep in datos["endpoints"]:

        def row(label, value):
            txt_clean = clean_text(value)
            lines = pdf.multi_cell(145, 6, txt_clean, split_only=True)
            alt_celda = max(len(lines) * 6, 6)
            
            x = pdf.get_x()
            y = pdf.get_y()
            
            pdf.cell(45, alt_celda, label, 1)
            pdf.multi_cell(145, 6, txt_clean, 1)
            pdf.set_xy(x, y + alt_celda)

        row("URL", ep["url"])
        row("Descripción", ep["desc"])
        row("Método", ep["metodo"])

        # Fila simétrica y autoajustable para BODY
        body_clean = clean_text(ep["body"])
        lines_body = pdf.multi_cell(145, 6, body_clean, split_only=True)
        alt_body = max(len(lines_body) * 6, 6)
        
        x_b = pdf.get_x()
        y_b = pdf.get_y()
        pdf.cell(45, alt_body, "Body", 1)
        pdf.multi_cell(145, 6, body_clean, 1)
        pdf.set_xy(x_b, y_b + alt_body)

        row("Escenario", ep["escenario"])
        row("Precondición", ep["precon"])

        # Fila simétrica y autoajustable para RESPONSE
        resp_clean = clean_text(ep["resp"])
        lines_resp = pdf.multi_cell(145, 6, resp_clean, split_only=True)
        alt_resp = max(len(lines_resp) * 6, 6)
        
        x_r = pdf.get_x()
        y_r = pdf.get_y()
        pdf.cell(45, alt_resp, "Response", 1)
        pdf.multi_cell(145, 6, resp_clean, 1)
        pdf.set_xy(x_r, y_r + alt_resp)

        # Fila simétrica y autoajustable para ACLARACIONES (Se dibuja si tiene texto)
        if ep["aclaracion"].strip():
            aclar_clean = clean_text(ep["aclaracion"])
            lines_aclar = pdf.multi_cell(145, 6, aclar_clean, split_only=True)
            alt_aclar = max(len(lines_aclar) * 6, 6)
            
            x_a = pdf.get_x()
            y_a = pdf.get_y()
            pdf.cell(45, alt_aclar, "Aclaraciones", 1)
            pdf.multi_cell(145, 6, aclar_clean, 1)
            pdf.set_xy(x_a, y_a + alt_aclar)

        pdf.ln(3)

    return pdf.output(dest="S").encode("latin-1")


# =========================================================
# UI PRINCIPAL
# =========================================================
st.title("QA_Helper")

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ QA Suite IA",
    "📄 DPR Claro",
    "🧰 Tools",
    "💬 Chat IA"
])

# =========================================================
# TAB 1 - IA AUTOMATION
# =========================================================
with tab1:

    st.markdown("""
## ℹ️ ¿Qué hace cada opción?

- Casos de Prueba → QA manual estructurado  
- Cypress → JS. 
- Playwright → JS. 
- Selenium → Python.
- JSON API → Postman  
""")

    tipo = st.selectbox("Tipo", [
        "Casos de Prueba",
        "Cypress",
        "Playwright (JS)",
        "Selenium (Python)",
        "JSON API"
    ])

    contexto = st.text_area("Contexto")

    if st.button("Generar"):

        system = """
Eres QA Automation Senior.

- Cypress → JS
- Playwright → JS
- Selenium → Python
- JSON API → JSON request
- Casos → test cases

RESPONDER CON CODIGO LISTO PARA USAR.
"""

        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"{tipo}\n{contexto}"}
            ]
        ).choices[0].message.content

        st.session_state.last_ai = res

        st.code(res)

        st.download_button(
            "⬇️ Descargar output",
            res,
            file_name=f"{tipo}.txt"
        )


# =========================================================
# TAB 2 - DPR CLARO
# =========================================================
with tab2:

    h_fecha = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))
    h_version = st.text_input("Versión", "1.0")
    h_desc = st.text_input("Descripción", "DPR")
    h_autor = st.text_input("Autor", "QA")

    # Nueva UI con Checkboxes ordenados en dos columnas
    st.markdown("##### Seleccione los tipos de prueba para la Descripción:")
    opciones_desc = ["Carga", "Stress", "Benchmark", "Confiabilidad", "Pico", "Capacidad"]
    desc_seleccionadas = []
    
    col_chk1, col_chk2 = st.columns(2)
    for idx, opt in enumerate(opciones_desc):
        with col_chk1 if idx % 2 == 0 else col_chk2:
            if st.checkbox(opt, key=f"chk_desc_{opt}"):
                desc_seleccionadas.append(opt)

    st.write("") 
    objetivo = st.text_area("Objetivo")
    alcance = st.text_area("Alcance")
    swaggers = st.text_area("Swaggers")

    if "eps" not in st.session_state:
        st.session_state.eps = 1

    endpoints = []

    for i in range(st.session_state.eps):
        st.markdown(f"### Endpoint {i+1}")

        url = st.text_input("URL", key=f"url{i}")
        desc = st.text_input("Desc", key=f"desc{i}")
        met = st.selectbox("Método", ["GET","POST","PUT","DELETE"], key=f"met{i}")
        body = st.text_area("Body", key=f"body{i}")
        esc = st.text_input("Escenario", key=f"esc{i}")
        pre = st.text_input("Precondición", key=f"pre{i}")
        resp = st.text_area("Response", key=f"resp{i}")
        # Campo nuevo de aclaraciones para cada endpoint
        aclaracion = st.text_area("Aclaraciones / Notas adicionales (Opcional)", key=f"aclaracion{i}")

        endpoints.append({
            "url": url,
            "desc": desc,
            "metodo": met,
            "body": body,
            "escenario": esc,
            "precon": pre,
            "resp": resp,
            "aclaracion": aclaracion
        })

    if st.button("Agregar endpoint"):
        st.session_state.eps += 1
        st.rerun()

    if st.button("Generar PDF"):
        pdf = generar_pdf({
            "h_fecha": h_fecha,
            "h_version": h_version,
            "h_desc": h_desc,
            "h_autor": h_autor,
            "descripcion_list": desc_seleccionadas,
            "objetivo": objetivo,
            "alcance": alcance,
            "swaggers": swaggers,
            "endpoints": endpoints
        })

        st.download_button(
            "Descargar DPR",
            pdf,
            "DPR.pdf",
            "application/pdf"
        )


# =========================================================
# TAB 3 - TOOLS
# =========================================================
with tab3:
    st.subheader("⚖️ Comparador de JSON")
    st.caption("Compara dos JSON campo por campo y detecta diferencias, faltantes y cambios.")
    t1 = st.text_area("Texto 1")
    t2 = st.text_area("Texto 2")

    if st.button("Comparar"):
        diff = difflib.Differ().compare(t1.splitlines(), t2.splitlines())
        st.code("\n".join(diff), "diff")

    b64 = st.text_area("Base64")

    if st.button("Decode"):
        st.code(base64.b64decode(b64).decode())


# =========================================================
# TAB 4 - CHAT
# =========================================================
with tab4:

    q = st.text_area("Consulta")

    if st.button("Enviar"):
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Ayuda QA"},
                {"role": "user", "content": q}
            ]
        ).choices[0].message.content

        st.info(r)


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.write("© Mayo 2026 -| Nicolas Dondo", "nicodondo1980@gmail.com")