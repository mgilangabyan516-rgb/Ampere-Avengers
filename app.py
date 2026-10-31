import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
from pathlib import Path

from model import FEATURES, train_demo_model, predict_status
from storage import init_db, save_reading, load_readings

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="AquaDrain-AI | Pipeline Monitoring",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

ASSET_DIR = Path(__file__).parent / "assets"

# =========================================================
# CORPORATE LIGHT THEME
# =========================================================
st.markdown(
    """
    <style>
    :root { --navy:#102B46; --blue:#176FC1; --cyan:#35B8D8; --ink:#17324D; --muted:#667B91; --line:#DCE6F0; --canvas:#EEF3F9; }
    .stApp { background:var(--canvas); color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(238,243,249,.96); }
    .block-container { max-width:1500px; padding-top:1.35rem; padding-bottom:2.5rem; }

    /* Sidebar navy: readable text and controls */
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#102B46 0%,#153B5E 100%); border-right:1px solid #234C70; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#EAF3FB !important; }
    [data-testid="stSidebar"] hr { border-color:rgba(220,237,250,.20); }
    [data-testid="stSidebar"] [role="radiogroup"] label { background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.10); border-radius:9px; padding:.42rem .55rem; margin:.18rem 0; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(53,184,216,.16); }

    .topbar { background:#fff; border:1px solid var(--line); border-radius:15px; padding:.65rem 1rem; margin-bottom:1rem; box-shadow:0 3px 12px rgba(16,43,70,.045); }
    .partner-label { color:#71849A; font-size:.65rem; text-transform:uppercase; letter-spacing:.09em; font-weight:750; text-align:center; margin-bottom:.2rem; }
    .brand-copy { padding:.3rem .15rem; }
    .brand-copy .eyebrow { color:var(--blue); font-size:.68rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
    .brand-copy .name { color:var(--navy); font-size:1.55rem; font-weight:850; line-height:1.2; }
    .brand-copy .sub { color:var(--muted); font-size:.82rem; }

    .hero { position:relative; overflow:hidden; background:linear-gradient(105deg,#102B46 0%,#16466E 62%,#176B91 100%); border-radius:17px; padding:1.75rem 2rem; color:white; margin:.25rem 0 1.05rem; box-shadow:0 7px 20px rgba(16,43,70,.12); min-height:180px; }
    .hero:after { content:""; position:absolute; right:-55px; top:-100px; width:390px; height:390px; border-radius:50%; border:34px solid rgba(90,196,224,.12); box-shadow:0 0 0 24px rgba(90,196,224,.055),0 0 0 54px rgba(90,196,224,.035); }
    .hero-kicker { color:#9BDDF0; font-size:.72rem; letter-spacing:.14em; font-weight:800; text-transform:uppercase; }
    .hero-title { color:white; font-size:clamp(1.65rem,3.2vw,2.55rem); font-weight:820; line-height:1.15; margin:.45rem 0 .55rem; }
    .hero-copy { color:#E4F0F8; font-size:.94rem; max-width:720px; line-height:1.55; }
    .section-note { color:var(--muted); margin-top:-.55rem; margin-bottom:1rem; font-size:.88rem; }

    div[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:13px; padding:13px 15px; box-shadow:0 3px 12px rgba(16,43,70,.035); }
    div.stButton > button[kind="primary"] { background:#176FC1; border:1px solid #176FC1; border-radius:9px; font-weight:700; padding:.52rem 1rem; }
    div.stButton > button[kind="primary"]:hover { background:#125A9E; border-color:#125A9E; }
    h1,h2,h3 { color:var(--navy); }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:10px; overflow:hidden; }
    footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# MODEL
# =========================================================
@st.cache_resource
def get_model():
    return train_demo_model()

model, demo_metrics = get_model()

# =========================================================
# HEADER AND LOGOS
# =========================================================
logo_col, title_col, huawei_col, upi_col = st.columns([1.0, 3.4, 1.1, 1.1])
with logo_col:
    logo_path = ASSET_DIR / "aquadrain_logo.png"
    if logo_path.exists(): st.image(str(logo_path), width=112)
    else: st.markdown("**AquaDrain-AI**")
with title_col:
    st.markdown(
        '<div class="brand-copy"><div class="eyebrow">Innovation Project</div><div class="name">AquaDrain-AI</div><div class="sub">AI-Powered Pipeline Monitoring System</div></div>',
        unsafe_allow_html=True,
    )
with huawei_col:
    st.markdown('<div class="partner-label">Technology learning</div>', unsafe_allow_html=True)
    logo_path = ASSET_DIR / "huawei_logo.png"
    if logo_path.exists(): st.image(str(logo_path), width=82)
    else: st.markdown("**Huawei ICT Academy**")
with upi_col:
    st.markdown('<div class="partner-label">Institution</div>', unsafe_allow_html=True)
    logo_path = ASSET_DIR / "upi_logo.png"
    if logo_path.exists(): st.image(str(logo_path), width=82)
    else: st.markdown("**UPI**")

st.markdown(
    '<section class="hero"><div class="hero-kicker">Smart Water Infrastructure</div><div class="hero-title">Detect Early. Prevent Greater Loss.</div><div class="hero-copy">Sistem pemantauan tekanan dan debit air berbasis Artificial Intelligence untuk membantu mengidentifikasi indikasi kebocoran pada jaringan perpipaan.</div></section>',
    unsafe_allow_html=True,
)
st.info("Prototype demonstrasi: model saat ini menggunakan data sintetis. Hasil prediksi belum menjadi validasi kebocoran pada jaringan pipa nyata.")

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    logo_path = ASSET_DIR / "aquadrain_logo.png"
    if logo_path.exists(): st.image(str(logo_path), width=118)
    st.markdown("## AquaDrain-AI")
    st.caption("Three Minds. One Innovation.")
    st.divider()
    st.markdown("### Navigasi Data")
    mode = st.radio("Pilih sumber data", ["Simulasi manual", "Unggah CSV", "Data ESP32 (API)"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Satuan pengukuran**")
    st.caption("Tekanan: bar\n\nDebit: L/menit")
    st.divider()
    st.caption("SMART WATER INFRASTRUCTURE")
    st.caption("Detect Early. Prevent Greater Loss.")

# =========================================================
# MAIN CONTENT
# =========================================================
st.subheader("Monitoring & Analysis")
st.markdown(
    '<div class="section-note">Pilih sumber data untuk melihat indikasi kondisi jaringan pipa.</div>',
    unsafe_allow_html=True,
)

if mode == "Simulasi manual":
    st.markdown("### Parameter Sensor")
    c1, c2, c3, c4 = st.columns(4)

    p1 = c1.number_input("Tekanan 1 (bar)", min_value=0.0, value=2.8, step=0.1)
    p2 = c2.number_input("Tekanan 2 (bar)", min_value=0.0, value=2.6, step=0.1)
    f1 = c3.number_input("Debit 1 (L/min)", min_value=0.0, value=8.0, step=0.1)
    f2 = c4.number_input("Debit 2 (L/min)", min_value=0.0, value=7.9, step=0.1)

    pump = st.selectbox(
        "Status pompa",
        [1, 0],
        format_func=lambda x: "ON" if x == 1 else "OFF",
    )

    row = {
        "pressure_1": p1,
        "pressure_2": p2,
        "flow_1": f1,
        "flow_2": f2,
        "pump_status": pump,
    }

    if st.button("Analisis dan Simpan Data", type="primary"):
        status, prob = predict_status(model, row)
        row["timestamp"] = datetime.now(timezone.utc).isoformat()
        save_reading(row, source="manual")
        st.session_state["last_prediction"] = (status, prob)

    if "last_prediction" in st.session_state:
        status, prob = st.session_state["last_prediction"]
        st.markdown("### Hasil Analisis Terakhir")
        r1, r2 = st.columns(2)
        r1.metric("Status model", status)
        r2.metric("Skor indikasi model", f"{prob:.1%}")
        st.caption(
            "Skor ini bukan probabilitas kebocoran yang sudah terkalibrasi; "
            "hanya skor model demonstrasi."
        )

elif mode == "Unggah CSV":
    st.markdown("### Analisis Dataset Sensor")
    st.write(
        "Kolom wajib: `pressure_1`, `pressure_2`, `flow_1`, `flow_2`, "
        "`pump_status`. Kolom `timestamp` bersifat opsional."
    )
    upload = st.file_uploader("Pilih file CSV", type=["csv"])

    if upload:
        df = pd.read_csv(upload)
        missing = [column for column in FEATURES if column not in df.columns]

        if missing:
            st.error("Kolom belum lengkap: " + ", ".join(missing))
        else:
            st.dataframe(df.head(20), use_container_width=True)

            if st.button("Analisis Seluruh Baris", type="primary"):
                results = []
                for _, sensor_row in df.iterrows():
                    status, prob = predict_status(model, sensor_row)
                    results.append({"status": status, "model_score": prob})
                    timestamp = (
                        sensor_row["timestamp"]
                        if "timestamp" in df.columns
                        else datetime.now(timezone.utc).isoformat()
                    )
                    save_reading(
                        {
                            **{column: sensor_row[column] for column in FEATURES},
                            "timestamp": timestamp,
                        },
                        source="CSV",
                    )

                output = pd.concat(
                    [df.reset_index(drop=True), pd.DataFrame(results)],
                    axis=1,
                )
                st.dataframe(output, use_container_width=True)
                st.download_button(
                    "Unduh Hasil Analisis CSV",
                    output.to_csv(index=False),
                    "aquadrain_analysis.csv",
                    "text/csv",
                )

else:
    st.markdown("### Koneksi Data ESP32")
    st.write(
        "Untuk pengujian lokal, jalankan API dengan perintah berikut "
        "pada komputer yang menjalankan backend:"
    )
    st.code(
        "uvicorn api:app --host 0.0.0.0 --port 8000",
        language="bash",
    )
    st.write("Contoh endpoint penerimaan data:")
    st.code("POST http://ALAMAT-IP-LAPTOP:8000/sensor", language="text")
    st.code(
        '{"pressure_1":2.8,"pressure_2":2.6,"flow_1":8.0,'
        '"flow_2":7.9,"pump_status":1}',
        language="json",
    )
    st.warning(
        "Deployment Streamlit Cloud tidak otomatis terhubung ke API lokal "
        "di laptop. Integrasi ESP32 jarak jauh memerlukan backend yang "
        "dihosting terpisah."
    )

# =========================================================
# MONITORING HISTORY
# =========================================================
st.divider()
st.subheader("Riwayat Monitoring")
history = load_readings(1000)

if history.empty:
    st.warning(
        "Belum ada data. Masukkan simulasi, unggah CSV, atau kirim data dari ESP32."
    )
else:
    latest = history.iloc[-1]
    a, b, c = st.columns(3)
    a.metric("Jumlah Data Tersimpan", len(history))
    b.metric("Tekanan Titik 1", f"{latest.pressure_1:.2f} bar")
    c.metric("Debit Titik 1", f"{latest.flow_1:.2f} L/min")

    pressure_chart = px.line(
        history,
        x="timestamp",
        y=["pressure_1", "pressure_2"],
        title="Tren Tekanan Air",
        labels={"value": "Tekanan (bar)", "timestamp": "Waktu", "variable": "Sensor"},
        color_discrete_sequence=["#1689B8", "#123B5D"],
    )
    pressure_chart.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color="#183247",
        legend_title_text="",
    )
    st.plotly_chart(pressure_chart, use_container_width=True)

    flow_chart = px.line(
        history,
        x="timestamp",
        y=["flow_1", "flow_2"],
        title="Tren Debit Air",
        labels={"value": "Debit (L/min)", "timestamp": "Waktu", "variable": "Sensor"},
        color_discrete_sequence=["#1689B8", "#123B5D"],
    )
    flow_chart.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color="#183247",
        legend_title_text="",
    )
    st.plotly_chart(flow_chart, use_container_width=True)

    st.markdown("### Data Terbaru")
    st.dataframe(history.tail(30), use_container_width=True)
    st.download_button(
        "Unduh Riwayat CSV",
        history.to_csv(index=False),
        "aquadrain_history.csv",
        "text/csv",
    )

# =========================================================
# MODEL INFORMATION AND PROJECT FOOTER
# =========================================================
with st.expander("Evaluasi Model Demonstrasi"):
    st.write(
        "Model saat ini dilatih dari data sintetis untuk menunjukkan alur software. "
        "Angka di bawah bukan hasil uji lapangan."
    )
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accuracy", f"{demo_metrics['accuracy']:.1%}")
    m2.metric("Precision", f"{demo_metrics['precision']:.1%}")
    m3.metric("Recall", f"{demo_metrics['recall']:.1%}")
    m4.metric("F1-score", f"{demo_metrics['f1']:.1%}")
    st.write(
        "Confusion matrix (baris = label aktual [normal, leak], "
        "kolom = prediksi [normal, leak]):"
    )
    st.write(demo_metrics["confusion"])

st.divider()
st.markdown(
    """
    <div style="text-align:center; padding:0.8rem 0 0.3rem 0; color:#617789;">
      <div style="font-weight:800; color:#123B5D;">AquaDrain-AI</div>
      <div style="font-size:0.82rem;">
        AI-Powered Pipeline Monitoring System · Innovation Prototype
      </div>
      <div style="font-size:0.72rem; margin-top:0.35rem;">
        Huawei and UPI logos are displayed for project identification only.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
