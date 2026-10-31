import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timezone
from model import FEATURES, make_demo_dataset, train_demo_model, predict_status
from storage import init_db, save_reading, load_readings

st.set_page_config(page_title="AquaDrain-AI", page_icon="💧", layout="wide")
init_db()

@st.cache_resource
def get_model():
    return train_demo_model()

model, demo_metrics = get_model()

st.title("💧 AquaDrain-AI")
st.caption("Prototype dashboard — early indication of possible pipeline leakage")
st.info("Mode demonstrasi menggunakan data sintetis. Hasil prediksi belum tervalidasi untuk jaringan pipa nyata.")

with st.sidebar:
    st.header("Input Data")
    mode = st.radio("Pilih sumber data", ["Simulasi manual", "Unggah CSV", "Data ESP32 (API)"])
    st.divider()
    st.caption("Satuan contoh: tekanan dalam bar, debit dalam L/menit. Gunakan satuan yang konsisten.")

if mode == "Simulasi manual":
    st.subheader("Simulasi pembacaan sensor")
    c1, c2, c3, c4 = st.columns(4)
    p1 = c1.number_input("Tekanan 1 (bar)", min_value=0.0, value=2.8, step=0.1)
    p2 = c2.number_input("Tekanan 2 (bar)", min_value=0.0, value=2.6, step=0.1)
    f1 = c3.number_input("Debit 1 (L/min)", min_value=0.0, value=8.0, step=0.1)
    f2 = c4.number_input("Debit 2 (L/min)", min_value=0.0, value=7.9, step=0.1)
    pump = st.selectbox("Status pompa", [1, 0], format_func=lambda x: "ON" if x == 1 else "OFF")
    row = {"pressure_1": p1, "pressure_2": p2, "flow_1": f1, "flow_2": f2, "pump_status": pump}
    if st.button("Analisis dan simpan data", type="primary"):
        status, prob = predict_status(model, row)
        row["timestamp"] = datetime.now(timezone.utc).isoformat()
        save_reading(row, source="manual")
        st.session_state["last_prediction"] = (status, prob)
    if "last_prediction" in st.session_state:
        status, prob = st.session_state["last_prediction"]
        st.metric("Hasil analisis terakhir", status)
        st.write(f"Skor indikasi kebocoran model: **{prob:.1%}**")
        st.caption("Skor ini bukan probabilitas kebocoran yang sudah terkalibrasi; hanya skor model demonstrasi.")

elif mode == "Unggah CSV":
    st.subheader("Unggah dataset sensor")
    st.write("Kolom wajib: pressure_1, pressure_2, flow_1, flow_2, pump_status. Kolom timestamp opsional.")
    upload = st.file_uploader("Pilih file CSV", type=["csv"])
    if upload:
        df = pd.read_csv(upload)
        missing = [c for c in FEATURES if c not in df.columns]
        if missing:
            st.error("Kolom belum lengkap: " + ", ".join(missing))
        else:
            st.dataframe(df.head(20), use_container_width=True)
            if st.button("Analisis seluruh baris"):
                results = []
                for _, r in df.iterrows():
                    status, prob = predict_status(model, r)
                    results.append({"status": status, "model_score": prob})
                    ts = r["timestamp"] if "timestamp" in df.columns else datetime.now(timezone.utc).isoformat()
                    save_reading({**{k: r[k] for k in FEATURES}, "timestamp": ts}, source="CSV")
                out = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
                st.dataframe(out, use_container_width=True)
                st.download_button("Unduh hasil analisis CSV", out.to_csv(index=False), "aquadrain_analysis.csv", "text/csv")

else:
    st.subheader("Koneksi data ESP32")
    st.write("Jalankan API lokal dengan perintah `uvicorn api:app --host 0.0.0.0 --port 8000`, lalu arahkan ESP32 ke alamat IP laptop pada endpoint `/sensor`.")
    st.code("POST http://ALAMAT-IP-LAPTOP:8000/sensor", language="text")
    st.code('{"pressure_1":2.8,"pressure_2":2.6,"flow_1":8.0,"flow_2":7.9,"pump_status":1}', language="json")
    st.caption("Dashboard membaca data yang diterima API dari database lokal.")

st.divider()
st.subheader("Riwayat Monitoring")
history = load_readings(1000)
if history.empty:
    st.warning("Belum ada data. Masukkan simulasi, unggah CSV, atau kirim data dari ESP32.")
else:
    latest = history.iloc[-1]
    a, b, c = st.columns(3)
    a.metric("Jumlah data tersimpan", len(history))
    b.metric("Tekanan titik 1", f"{latest.pressure_1:.2f} bar")
    c.metric("Debit titik 1", f"{latest.flow_1:.2f} L/min")
    fig = px.line(history, x="timestamp", y=["pressure_1", "pressure_2"], title="Tren Tekanan Air")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.line(history, x="timestamp", y=["flow_1", "flow_2"], title="Tren Debit Air")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(history.tail(30), use_container_width=True)
    st.download_button("Unduh riwayat CSV", history.to_csv(index=False), "aquadrain_history.csv", "text/csv")

with st.expander("Evaluasi model demonstrasi"):
    st.write("Model saat ini dilatih dari data sintetis untuk menunjukkan alur software. Angka di bawah bukan hasil uji lapangan.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accuracy", f"{demo_metrics['accuracy']:.1%}")
    m2.metric("Precision", f"{demo_metrics['precision']:.1%}")
    m3.metric("Recall", f"{demo_metrics['recall']:.1%}")
    m4.metric("F1-score", f"{demo_metrics['f1']:.1%}")
    st.write("Confusion matrix (baris = label aktual [normal, leak], kolom = prediksi [normal, leak]):")
    st.write(demo_metrics["confusion"])
