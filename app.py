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
    :root {
        --navy: #123B5D;
        --blue: #1689B8;
        --pale: #EAF4F8;
        --ink: #183247;
        --muted: #617789;
    }

    .stApp {
        background: #F7FAFC;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(247, 250, 252, 0.92);
    }

    [data-testid="stSidebar"] {
        background: #EDF4F8;
        border-right: 1px solid #D9E6ED;
    }

    .block-container {
        padding-top: 1.7rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .brand-strip {
        background: linear-gradient(105deg, #123B5D 0%, #176D91 58%, #1689B8 100%);
        padding: 1.55rem 1.8rem;
        border-radius: 18px;
        color: white;
        margin: 0.35rem 0 1.1rem 0;
        box-shadow: 0 8px 24px rgba(18, 59, 93, 0.12);
    }

    .brand-kicker {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        opacity: 0.82;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .brand-title {
        font-size: clamp(2rem, 4vw, 3rem);
        line-height: 1.08;
        font-weight: 800;
        margin: 0;
        color: white;
    }

    .brand-subtitle {
        font-size: 1rem;
        margin-top: 0.55rem;
        color: #E7F5FB;
        max-width: 760px;
    }

    .partner-label {
        color: #617789;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.4rem;
    }

    .logo-fallback {
        border: 1px solid #D9E6ED;
        background: white;
        border-radius: 12px;
        min-height: 68px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.65rem;
        color: #29485E;
        font-weight: 750;
        text-align: center;
    }

    .section-intro {
        color: #617789;
        margin-top: -0.55rem;
        margin-bottom: 1rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #DCE8EE;
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 3px 12px rgba(18, 59, 93, 0.04);
    }

    div.stButton > button[kind="primary"] {
        background: #1689B8;
        border: 1px solid #1689B8;
        border-radius: 10px;
        font-weight: 700;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #116F98;
        border-color: #116F98;
    }

    h1, h2, h3 {
        color: #123B5D;
    }

    footer {visibility: hidden;}
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
logo_col, title_col, huawei_col, upi_col = st.columns([1.0, 3.8, 1.15, 1.0])

with logo_col:
    logo_path = ASSET_DIR / "aquadrain_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=105)
    else:
        st.markdown(
            '<div class="logo-fallback">💧<br>AquaDrain-AI</div>',
            unsafe_allow_html=True,
        )

with title_col:
    st.markdown(
        """
        <div style="padding: 0.35rem 0.2rem;">
          <div style="font-size:0.76rem; color:#1689B8; font-weight:800;
                      letter-spacing:0.13em; text-transform:uppercase;">
            Innovation Project
          </div>
          <div style="font-size:1.65rem; color:#123B5D; font-weight:850;">
            AquaDrain-AI
          </div>
          <div style="font-size:0.9rem; color:#617789;">
            AI-Powered Pipeline Monitoring System
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with huawei_col:
    st.markdown('<div class="partner-label">Technology context</div>', unsafe_allow_html=True)
    logo_path = ASSET_DIR / "huawei_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown('<div class="logo-fallback">HUAWEI</div>', unsafe_allow_html=True)

with upi_col:
    st.markdown('<div class="partner-label">Institution</div>', unsafe_allow_html=True)
    logo_path = ASSET_DIR / "upi_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown('<div class="logo-fallback">UPI</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="brand-strip">
      <div class="brand-kicker">Smart Water Infrastructure</div>
      <div class="brand-title">Detect Early. Prevent Greater Loss.</div>
      <div class="brand-subtitle">
        Sistem pemantauan tekanan dan debit air berbasis Artificial Intelligence
        untuk membantu mengidentifikasi indikasi kebocoran pada jaringan perpipaan.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Status prototype: mode demonstrasi menggunakan data sintetis. "
    "Hasil prediksi belum tervalidasi untuk jaringan pipa nyata."
)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 💧 AquaDrain-AI")
    st.caption("Pipeline Monitoring Dashboard")
    st.divider()
    st.header("Input Data")
    mode = st.radio(
        "Pilih sumber data",
        ["Simulasi manual", "Unggah CSV", "Data ESP32 (API)"],
    )
    st.divider()
    st.caption(
        "Satuan contoh: tekanan dalam bar, debit dalam L/menit. "
        "Gunakan satuan yang konsisten."
    )
    st.caption("Corporate Light Interface")

# =========================================================
# MAIN CONTENT
# =========================================================
st.subheader("Monitoring & Analysis")
st.markdown(
    '<div class="section-intro">Pilih sumber data untuk melihat indikasi kondisi jaringan pipa.</div>',
    unsafe_allow_html=True,
)

if mode == "Simulasi manual":
    st.markdown("### Simulasi Pembacaan Sensor")
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
