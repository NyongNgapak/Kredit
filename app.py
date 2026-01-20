import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

st.set_page_config(
    page_title="Sistem Pakar Kredit",
    page_icon="🏦",
    layout="centered"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #00C1D4;
        margin-bottom: 10px;
        font-weight: 600;
    }
    .result-card {
        background-color: #1E2233;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 193, 212, 0.15);
        margin-top: 20px;
        border: 1px solid #3A3F55;
    }
    .metric-box {
        font-size: 1.3em;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        color: #E0E0E0;
    }
    .stButton > button {
        background-color: #00C1D4;
        color: #2A2D3A;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #00a8b8;
        color: white;
    }
    .stInfo {
        background-color: rgba(0, 193, 212, 0.15) !important;
        color: #E0E0E0 !important;
        border-left: 4px solid #00C1D4 !important;
    }
    .stSuccess { background-color: rgba(76, 175, 80, 0.15) !important; border-left: 4px solid #4CAF50 !important; }
    .stWarning { background-color: rgba(255, 167, 38, 0.15) !important; border-left: 4px solid #FFA726 !important; }
    .stError { background-color: rgba(239, 83, 80, 0.15) !important; border-left: 4px solid #EF5350 !important; }
    hr {
        border-color: #3A3F55;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🏦 Sistem Pakar Pemberian Kredit</h1>', unsafe_allow_html=True)
st.caption("Metode Fuzzy Mamdani + Analisis DBR Otomatis (Khusus Koperasi Karyawan)")

status = ctrl.Antecedent(np.arange(0, 11, 1), 'status')
lama = ctrl.Antecedent(np.arange(0, 11, 1), 'lama')
gaji = ctrl.Antecedent(np.arange(0, 21, 0.1), 'gaji')
jaminan = ctrl.Antecedent(np.arange(0, 11, 1), 'jaminan')
pinjaman = ctrl.Antecedent(np.arange(0, 51, 1), 'pinjaman')
dbr = ctrl.Antecedent(np.arange(0, 101, 1), 'dbr')

kelayakan = ctrl.Consequent(np.arange(0, 101, 1), 'kelayakan')

status['rendah'] = fuzz.trimf(status.universe, [0, 0, 5])
status['sedang'] = fuzz.trimf(status.universe, [3, 5, 7])
status['tinggi'] = fuzz.trimf(status.universe, [5, 10, 10])

lama['rendah'] = fuzz.trimf(lama.universe, [0, 0, 4])
lama['sedang'] = fuzz.trimf(lama.universe, [3, 5, 7])
lama['tinggi'] = fuzz.trimf(lama.universe, [6, 10, 10])

gaji['rendah'] = fuzz.trimf(gaji.universe, [0, 3, 5])
gaji['sedang'] = fuzz.trimf(gaji.universe, [4, 7, 10])
gaji['tinggi'] = fuzz.trimf(gaji.universe, [9, 20, 20])

jaminan['buruk'] = fuzz.trimf(jaminan.universe, [0, 0, 4])
jaminan['sedang'] = fuzz.trimf(jaminan.universe, [3, 5, 7])
jaminan['baik'] = fuzz.trimf(jaminan.universe, [6, 10, 10])

pinjaman['rendah'] = fuzz.trimf(pinjaman.universe, [0, 10, 20])
pinjaman['sedang'] = fuzz.trimf(pinjaman.universe, [15, 25, 35])
pinjaman['tinggi'] = fuzz.trimf(pinjaman.universe, [30, 50, 50])

dbr['rendah'] = fuzz.trimf(dbr.universe, [0, 20, 30])
dbr['sedang'] = fuzz.trimf(dbr.universe, [30, 40, 50])
dbr['tinggi'] = fuzz.trimf(dbr.universe, [50, 70, 100])

kelayakan['tidak_layak'] = fuzz.trimf(kelayakan.universe, [0, 0, 50])
kelayakan['dipertimbangkan'] = fuzz.trimf(kelayakan.universe, [30, 50, 70])
kelayakan['layak'] = fuzz.trimf(kelayakan.universe, [60, 100, 100])

rules = [
    ctrl.Rule(status['rendah'], kelayakan['tidak_layak']),
    ctrl.Rule(jaminan['buruk'], kelayakan['tidak_layak']),
    ctrl.Rule(lama['rendah'], kelayakan['tidak_layak']),
    ctrl.Rule(gaji['rendah'], kelayakan['tidak_layak']),
    ctrl.Rule(dbr['tinggi'], kelayakan['tidak_layak']),
    
    ctrl.Rule(
        status['tinggi'] & lama['tinggi'] & gaji['tinggi'] & jaminan['baik'] & pinjaman['rendah'],
        kelayakan['layak']
    ),
    ctrl.Rule(
        gaji['tinggi'] & jaminan['baik'] & dbr['rendah'],
        kelayakan['layak']
    ),

    ctrl.Rule(
        (status['sedang'] | status['tinggi']) &
        (gaji['sedang'] | gaji['tinggi']) &
        (jaminan['sedang'] | jaminan['baik']) &
        (dbr['sedang'] | dbr['rendah']),
        kelayakan['dipertimbangkan']
    ),

    ctrl.Rule(
        status['sedang'] & lama['sedang'] & gaji['sedang'] & jaminan['sedang'],
        kelayakan['dipertimbangkan']
    )
]

kelayakan_ctrl = ctrl.ControlSystem(rules)
kelayakan_sim = ctrl.ControlSystemSimulation(kelayakan_ctrl)

st.markdown("### 📝 Masukkan Data Nasabah")

status_val = st.selectbox("Status Kepegawaian", ["Part-time", "Kontrak", "Tetap"])

lama_val = st.number_input(
    "Lama Bekerja (Tahun)",
    min_value=0,
    max_value=10,
    value=3,
    step=1
)

gaji_val = st.number_input(
    "Gaji per Bulan (juta)",
    min_value=0.0,
    max_value=20.0,
    value=5.0,
    step=0.1,
    format="%.1f"
)

jaminan_val = st.selectbox("Jenis Jaminan", [
    "Tidak Ada",
    "Potong Gaji Otomatis",
    "Jaminan Rekan Kerja",
    "BPKB Motor",
    "BPKB Mobil",
    "SHM Rumah",
    "Surat Jaminan Atasan"
])

pinjaman_val = st.number_input(
    "Pinjaman Diajukan (juta)",
    min_value=0.0,
    max_value=50.0,
    value=20.0,
    step=0.5,
    format="%.1f"
)

tenor = st.selectbox("Tenor Pinjaman (bulan)", [6, 12, 24, 36])

cicilan_lain_val = st.number_input(
    "Cicilan Lain (juta/bulan)",
    min_value=0.0,
    max_value=20.0,
    value=0.0,
    step=0.1,
    format="%.1f"
)

status_map = {"Part-time": 2, "Kontrak": 5, "Tetap": 8}
jaminan_map = {
    "Tidak Ada": 2,
    "Potong Gaji Otomatis": 9,
    "Jaminan Rekan Kerja": 5,
    "BPKB Motor": 4,
    "BPKB Mobil": 6,
    "SHM Rumah": 8,
    "Surat Jaminan Atasan": 7
}

if gaji_val <= 0:
    st.error("⚠️ Gaji tidak boleh nol atau negatif!")
    st.stop()
if pinjaman_val <= 0:
    st.error("⚠️ Pinjaman harus lebih dari 0!")
    st.stop()

estimasi_cicilan = pinjaman_val / tenor
total_cicilan = estimasi_cicilan + cicilan_lain_val
dbr_value = (total_cicilan / gaji_val) * 100

st.divider()
st.markdown("### 📊 Ringkasan Input & Risiko")
col3, col4 = st.columns(2)
with col3:
    st.info(f"📌 Estimasi Cicilan Pinjaman: **{estimasi_cicilan:.2f} jt/bulan**")
    st.info(f"📌 Cicilan Lain: **{cicilan_lain_val:.2f} jt/bulan**")
with col4:
    st.info(f"📌 Total Cicilan: **{total_cicilan:.2f} jt/bulan**")
    st.info(f"📌 Debt Burden Ratio (DBR): **{dbr_value:.1f}%**")

if dbr_value > 60:
    st.warning("⚠️ DBR melebihi 60% — risiko tinggi menurut OJK!")

if st.button("🔍 Proses Permohonan Kredit", use_container_width=True):
    try:
        kelayakan_sim.input['status'] = status_map[status_val]
        kelayakan_sim.input['lama'] = float(lama_val)
        kelayakan_sim.input['gaji'] = float(gaji_val)
        kelayakan_sim.input['jaminan'] = jaminan_map[jaminan_val]
        kelayakan_sim.input['pinjaman'] = float(pinjaman_val)
        kelayakan_sim.input['dbr'] = float(dbr_value)

        kelayakan_sim.compute()
        hasil = kelayakan_sim.output['kelayakan']

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("🎯 Hasil Evaluasi Kelayakan")
        st.progress(min(int(hasil), 100))
        st.markdown(f'<div class="metric-box">Nilai Kelayakan: {hasil:.1f}/100</div>', unsafe_allow_html=True)

        if hasil >= 60:
            st.success("✅ **Kredit Layak Disetujui**")
            st.write("Nasabah memiliki profil risiko rendah.")
        elif hasil >= 40:
            st.warning("⚠️ **Kredit Perlu Pertimbangan Lebih Lanjut**")
            st.write("Disarankan verifikasi tambahan atau jaminan pendukung.")
        else:
            st.error("❌ **Kredit Tidak Layak**")
            st.write("Profil risiko terlalu tinggi. Pertimbangkan penolakan.")

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses: {e}")

st.divider()
st.caption("💡 Sistem ini menggunakan logika fuzzy Mamdani dan dirancang khusus untuk koperasi karyawan.")