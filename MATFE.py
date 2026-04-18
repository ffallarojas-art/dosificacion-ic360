import streamlit as st
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
st.set_page_config(page_title="CALCULADORA IC360 SAC", layout="wide")

# Estilos CSS para replicar las "Cards" del CustomTkinter
st.markdown("""
    <style>
    .metric-card {
        background-color: #1c2128;
        border: 2px solid #30363d;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-title { font-size: 14px; font-weight: bold; margin-bottom: 10px; }
    .metric-value { font-size: 42px; font-family: 'Courier New', Courier, monospace; font-weight: bold; color: #f0f6fc; margin: 0; }
    .metric-unit { color: #8b949e; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Inicialización de estado de navegación
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ==========================================
# FUNCIONES DE EXPORTACIÓN
# ==========================================
def exportar_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    header_style = ParagraphStyle(name='H', fontSize=18, textColor=colors.HexColor("#1a1c2e"), alignment=1, spaceAfter=20)
    content.append(Paragraph("INFORME DE DOSIFICACIÓN ESTRUCTURAL - IC360", header_style))
    content.append(Paragraph(f"<b>Ingeniero Responsable:</b> Ing. Frank", styles['Normal']))
    content.append(Paragraph(f"<b>Resistencia:</b> {data['fc']} | <b>Volumen:</b> {data['v_final']:.3f} m3", styles['Normal']))
    content.append(Spacer(1, 20))

    table_data = [
        ['MATERIAL', 'CANTIDAD', 'UNIDAD'],
        ['Cemento', f"{data['cem']:.2f}", 'Bolsas'],
        ['Arena Gruesa', f"{data['are']:.2f}", 'Baldes'],
        ['Piedra Chancada', f"{data['pie']:.2f}", 'Baldes'],
        ['Agua', f"{data['agu']:.2f}", 'Baldes'],
        ['Aditivo', f"{data['adi']:.2f}", 'Litros']
    ]

    t = Table(table_data, colWidths=[200, 100, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1c2e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    content.append(t)
    doc.build(content)
    buffer.seek(0)
    return buffer

# ==========================================
# PANTALLA DE INICIO
# ==========================================
if st.session_state.page == 'home':
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>SISTEMA DE DOSIFICACIÓN</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Ingeniero Falla Rojas - Corporación IC360 SAC</p>", unsafe_allow_html=True)
    
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            fc = st.selectbox("Resistencia f'c:", list(DATA_ICG.keys()), index=2)
            desp = st.number_input("Desperdicio (%):", value=5.0)
        with col_b:
            vol = st.number_input("Volumen Neto (m3):", min_value=0.0, value=0.0, step=0.1)
            adi = st.selectbox("Aditivo:", ["Ninguno", "Plastificante", "Superplastificante"])

        if st.button("EJECUTAR CÁLCULOS", use_container_width=True):
            if vol > 0:
                v_final = vol * (1 + (desp / 100))
                d = DATA_ICG[fc]
                
                c_bol = v_final * d['cem']
                a_bal = (v_final * d['are']) * 37
                p_bal = (v_final * d['pie']) * 37
                w_bal = (v_final * d['agu']) * 37
                
                ml_b = 500 if "Super" in adi else (250 if "Plastificante" == adi else 0)
                adi_l = (c_bol * ml_b) / 1000

                st.session_state.data_reporte = {
                    "fc": fc, "vol": vol, "v_final": v_final, "desp": desp,
                    "cem": c_bol, "are": a_bal, "pie": p_bal, "agu": w_bal, "adi": adi_l, "adi_t": adi
                }
                st.session_state.page = 'results'
                st.rerun()
            else:
                st.error("Por favor, ingrese un volumen válido.")

# ==========================================
# PANTALLA DE RESULTADOS
# ==========================================
elif st.session_state.page == 'results':
    data = st.session_state.data_reporte
    
    col_h1, col_h2 = st.columns([3, 1])
    col_h1.title(f"RESULTADOS: f'c {data['fc']}")
    if col_h2.button("NUEVO CÁLCULO", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()

    st.divider()

    # Grid de Tarjetas
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'''<div class="metric-card"><div class="metric-title" style="color:#1f6aa5">CEMENTO</div>
                    <div class="metric-value">{data['cem']:.2f}</div><div class="metric-unit">BOLSAS</div></div>''', unsafe_allow_html=True)
        st.markdown(f'''<div class="metric-card"><div class="metric-title" style="color:#d35400">PIEDRA CHANCADA</div>
                    <div class="metric-value">{data['pie']:.2f}</div><div class="metric-unit">BALDES (20L)</div></div>''', unsafe_allow_html=True)
    
    with c2:
        st.markdown(f'''<div class="metric-card"><div class="metric-title" style="color:#c0392b">ARENA GRUESA</div>
                    <div class="metric-value">{data['are']:.2f}</div><div class="metric-unit">BALDES (20L)</div></div>''', unsafe_allow_html=True)
        st.markdown(f'''<div class="metric-card"><div class="metric-title" style="color:#2980b9">AGUA</div>
                    <div class="metric-value">{data['agu']:.2f}</div><div class="metric-unit">BALDES (20L)</div></div>''', unsafe_allow_html=True)

    if data['adi'] > 0:
        st.markdown(f'''<div class="metric-card" style="border-color:#27ae60"><div class="metric-title" style="color:#27ae60">ADITIVO ({data['adi_t']})</div>
                    <div class="metric-value">{data['adi']:.2f}</div><div class="metric-unit">LITROS</div></div>''', unsafe_allow_html=True)

    st.divider()
    
    pdf_buffer = exportar_pdf(data)
    st.download_button(
        label="EXPORTAR REPORTE PDF",
        data=pdf_buffer,
        file_name=f"Reporte_IC360_{data['fc']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )