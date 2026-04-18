import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import datetime

# ==========================================
# DATA TÉCNICA - FUENTE ICG
# ==========================================
DATA_ICG = {
    "140 kg/cm2": {"cem": 7.01, "are": 0.51, "pie": 0.64, "agu": 0.184},
    "175 kg/cm2": {"cem": 8.43, "are": 0.54, "pie": 0.55, "agu": 0.185},
    "210 kg/cm2": {"cem": 9.73, "are": 0.52, "pie": 0.53, "agu": 0.186},
    "245 kg/cm2": {"cem": 11.50, "are": 0.50, "pie": 0.51, "agu": 0.187},
    "280 kg/cm2": {"cem": 13.34, "are": 0.45, "pie": 0.51, "agu": 0.189}
}

# Configuración de Página
st.set_page_config(page_title="IC360 Concrete Pro", layout="wide", initial_sidebar_state="expanded")

# Estilo para mejorar la visualización de métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 40px; color: #58a6ff; }
    [data-testid="stMetricLabel"] { font-size: 18px; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #238636; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# NAVEGACIÓN Y ENTRADA (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("⚙️ PARÁMETROS DE DISEÑO")
    fc_key = st.selectbox("Resistencia f'c:", list(DATA_ICG.keys()), index=2)
    vol_neto = st.number_input("Volumen Neto (m3):", min_value=0.1, value=15.0, step=1.0)
    desperdicio = st.slider("Desperdicio (%):", 0, 15, 5)
    tipo_adi = st.selectbox("Tipo de Aditivo:", ["Ninguno", "Plastificante", "Superplastificante"])
    
    st.divider()
    st.info("Desarrollado para Corporación IC360 SAC por Ing. Falla Rojas")

# ==========================================
# LÓGICA DE CÁLCULO (POST-PROCESO)
# ==========================================
v_final = vol_neto * (1 + (desperdicio / 100))
d = DATA_ICG[fc_key]

c_bol = v_final * d['cem']
a_bal = (v_final * d['are']) * 37
p_bal = (v_final * d['pie']) * 37
w_bal = (v_final * d['agu']) * 37

ml_b = 500 if "Super" in tipo_adi else (250 if "Plastificante" == tipo_adi else 0)
adi_l = (c_bol * ml_b) / 1000

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
st.title("🏗️ Master Concrete Analyzer v9.0")
st.subheader(f"Dosificación para f'c {fc_key}")

# Fila 1: Resumen de Volumen
m1, m2 = st.columns(2)
m1.metric("Volumen Final (con desp.)", f"{v_final:.3f} m3")
m2.metric("Aditivo Requerido", f"{adi_l:.2f} Litros", delta=tipo_adi, delta_color="normal")

st.divider()

# Fila 2: Cuadrícula de Materiales en Baldes
st.markdown("### 📊 CANTIDADES TOTALES PARA OBRA")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("CEMENTO", f"{c_bol:.2f}", "BOLSAS")
with col2:
    st.metric("ARENA GRUESA", f"{a_bal:.2f}", "BALDES")
with col3:
    st.metric("PIEDRA CHANC.", f"{p_bal:.2f}", "BALDES")
with col4:
    st.metric("AGUA TOTAL", f"{w_bal:.2f}", "BALDES")

# ==========================================
# EXPORTACIÓN PDF (REPORTLAB)
# ==========================================
def generate_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph(f"INFORME TÉCNICO DE MEZCLA - IC360 SAC", styles['Title']))
    elements.append(Paragraph(f"<b>Responsable:</b> Ing. Falla Rojas", styles['Normal']))
    elements.append(Paragraph(f"<b>Proyecto:</b> Tesis BIM 5D / Obra Chiclayo", styles['Normal']))
    elements.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [
        ['ITEM', 'MATERIAL', 'CANTIDAD', 'UNIDAD'],
        ['01', 'Cemento (42.5kg)', f"{c_bol:.2f}", 'Bolsas'],
        ['02', 'Arena Gruesa', f"{a_bal:.2f}", 'Baldes (20L)'],
        ['03', 'Piedra Chancada', f"{p_bal:.2f}", 'Baldes (20L)'],
        ['04', 'Agua de Mezcla', f"{w_bal:.2f}", 'Baldes (20L)'],
        ['05', f'Aditivo {tipo_adi}', f"{adi_l:.2f}", 'Litros']
    ]
    
    table = Table(data, colWidths=[50, 150, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1c2e")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

st.divider()
if st.button("🛠️ GENERAR DOCUMENTO TÉCNICO PDF"):
    pdf_data = generate_pdf()
    st.download_button(
        label="⬇️ DESCARGAR REPORTE",
        data=pdf_data,
        file_name=f"Reporte_IC360_{fc_key}.pdf",
        mime="application/pdf"
    )