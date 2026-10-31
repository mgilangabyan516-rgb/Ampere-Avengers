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
