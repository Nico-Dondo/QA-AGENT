import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime
import difflib
import os


# =========================================================
# CONFIG APP
# =========================================================
st.set_page_config(
    page_title="QA Tools",
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
        '●': '*', '•': '*',
        '—': '-', '–': '-',
        '“': '"', '’': '"',
        '‘': "'", '’': "'",
        '…': '...'
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
# HELPERS PDF
# =========================================================
def add_section_title(pdf, title):
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, title, 1, 1)


def add_multicell_box(pdf, text, h=5):
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, h, clean_text(text), 1)
    pdf.ln(5)


def row(pdf, label, value):
    txt = clean_text(value)
    x = pdf.get_x()
    y = pdf.get_y()

    lines = pdf.multi_cell(145, 6, txt, split_only=True)
    height = max(len(lines) * 6, 6)

    pdf.set_xy(x, y)
    pdf.cell(45, height, label, 1)
    pdf.multi_cell(145, 6, txt, 1)


# =========================================================
# PDF DPR
# =========================================================
def generar_pdf(datos):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
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

    # 1. HISTORIAL
    add_section_title(pdf, "1. Historial")
    pdf.set_font("Arial", "", 8)
    pdf.cell(35, 7, "Fecha", 1)
    pdf.cell(25, 7, "Version", 1)
    pdf.cell(75, 7, "Descripcion", 1)
    pdf.cell(55, 7, "Autor", 1, 1)

    pdf.cell(35, 7, clean_text(datos["h_fecha"]), 1)
    pdf.cell(25, 7, clean_text(datos["h_version"]), 1)
    pdf.cell(75, 7, clean_text(datos["h_desc"]), 1)
    pdf.cell(55, 7, clean_text(datos["h_autor"]), 1, 1)

    pdf.ln(5)

    # 1.5 TIPOS DE PRUEBA
    add_section_title(pdf, "Tipos de Prueba Seleccionados")
    add_multicell_box(pdf, datos["tipos_prueba"])

    # 2. OBJETIVO
    add_section_title(pdf, "2. Objetivo")
    add_multicell_box(pdf, datos["objetivo"])

    # 3. ENDPOINTS
    add_section_title(pdf, "3. Endpoints")
    pdf.set_font("Arial", "", 8)

    for ep in datos["endpoints"]:
        row(pdf, "URL", ep["url"])
        row(pdf, "Metodo", ep["metodo"])
        row(pdf, "Body", ep["body"])
        row(pdf, "Response", ep["resp"])
        row(pdf, "Aclaraciones / Notas", ep["notas"])
        pdf.ln(3)

    return pdf.output(dest="S").encode("latin-1")


# =========================================================
# UI
# =========================================================
st.title("QA Tools")

tab1, tab2 = st.tabs([
    "📄 DPR Generator",
    "🧰 Tools"
])


# =========================================================
# TAB DPR
# =========================================================
with tab1:
    h_fecha = st.text_input(
        "Fecha",
        datetime.now().strftime("%d/%m/%Y")
    )

    h_version = st.text_input("Version", "1.0")
    h_desc = st.text_input("Descripcion", "DPR")
    h_autor = st.text_input("Autor", "QA")

    # --- SECCIÓN: TIPOS DE PRUEBA (AHORA TODOS DESMARCADOS) ---
    st.markdown("### Tipos de prueba")
    col_test1, col_test2 = st.columns(2)

    with col_test1:
        carga = st.checkbox("Carga")
        benchmark = st.checkbox("Benchmark")
        pico = st.checkbox("Pico")

    with col_test2:
        stress = st.checkbox("Stress")
        confiabilidad = st.checkbox("Confiabilidad")
        capacidad = st.checkbox("Capacidad")

    # Procesar las opciones seleccionadas
    tipos_seleccionados = []
    if carga: tipos_seleccionados.append("Carga")
    if benchmark: tipos_seleccionados.append("Benchmark")
    if pico: tipos_seleccionados.append("Pico")
    if stress: tipos_seleccionados.append("Stress")
    if confiabilidad: tipos_seleccionados.append("Confiabilidad")
    if capacidad: tipos_seleccionados.append("Capacidad")
    
    tipos_prueba_str = ", ".join(tipos_seleccionados) if tipos_seleccionados else "Ninguno"
    # -----------------------------------------------------------

    objetivo = st.text_area("Objetivo", height=120)

    if "eps" not in st.session_state:
        st.session_state.eps = 1

    endpoints = []

    for i in range(st.session_state.eps):
        st.markdown(f"### Endpoint {i+1}")

        url = st.text_input("URL", key=f"url{i}")

        met = st.selectbox(
            "Metodo",
            ["GET", "POST", "PUT", "DELETE"],
            key=f"met{i}"
        )

        body = st.text_area("Body", key=f"body{i}", height=100)
        resp = st.text_area("Response", key=f"resp{i}", height=100)
        notas = st.text_area("Aclaraciones / Notas", key=f"notas{i}", height=120)

        endpoints.append({
            "url": url,
            "metodo": met,
            "body": body,
            "resp": resp,
            "notas": notas
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
            "tipos_prueba": tipos_prueba_str,
            "objetivo": objetivo,
            "endpoints": endpoints
        })

        st.download_button(
            "Descargar DPR",
            pdf,
            "DPR.pdf",
            "application/pdf"
        )


# =========================================================
# TAB TOOLS
# =========================================================
with tab2:
    st.subheader("⚖️ Comparador JSON")

    t1 = st.text_area("JSON 1")
    t2 = st.text_area("JSON 2")

    if st.button("Comparar JSON"):
        diff = difflib.Differ().compare(
            t1.splitlines(),
            t2.splitlines()
        )
        st.code("\n".join(diff), "diff")

    st.divider()

    st.subheader("🔐 Base64 Decoder")

    b64 = st.text_area("Base64")

    if st.button("Decode Base64"):
        try:
            decoded = base64.b64decode(b64).decode()
            st.code(decoded)
        except Exception as e:
            st.error(f"Error: {e}")


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.write("© 2026 - Nicolas Dondo")