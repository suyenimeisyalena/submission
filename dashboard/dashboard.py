import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Dashboard Analisis Penyewaan Sepeda")
st.markdown('Berbagai Faktor yang Memengaruhi Jumlah Penyewaan Sepeda')

df_day = pd.read_csv('dashboard/df_day.csv')
df_hour = pd.read_csv('dashboard/df_hour.csv')

df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

# Membuat pilihan tahun di sidebar
st.sidebar.header("Pilih Tahun Performa")
df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

pilihan_tahun = st.sidebar.selectbox(
    "Pilih Tahun yang Ingin Ditampilkan:",
    ["Gabungan Tahun 2011 & 2012", "2011", "2012"]
)

if pilihan_tahun == "2011":
    main_df_day = df_day[df_day['dteday'].dt.year == 2011].copy()
    main_df_hour = df_hour[df_hour['dteday'].dt.year == 2011].copy()
    
elif pilihan_tahun == "2012":
    main_df_day = df_day[df_day['dteday'].dt.year == 2012].copy()
    main_df_hour = df_hour[df_hour['dteday'].dt.year == 2012].copy()
    
else:
    main_df_day = df_day.copy()
    main_df_hour = df_hour.copy()

# Pilihan Status Hari
st.sidebar.header("Pilih Status Hari")
pilihan_hari = st.sidebar.selectbox(
    "Pilih Status Hari yang Ingin Ditampilkan:",
    ["Semua Hari", "Hari Kerja", "Hari Libur / Weekend"]
)
if pilihan_hari == "Hari Kerja":
    main_df_day = main_df_day[main_df_day['workingday'] == 1]
    main_df_hour = main_df_hour[main_df_hour['workingday'] == 1]
    
elif pilihan_hari == "Hari Libur / Weekend":
    main_df_day = main_df_day[main_df_day['workingday'] == 0]
    main_df_hour = main_df_hour[main_df_hour['workingday'] == 0]
    
else:
    pass

# Tampilan Utama
st.subheader("Ringkasan Mengenai Performa Data")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Total Seluruh Penyewaan Sepeda", value=f"{main_df_day['cnt'].sum():,}")
with col2:
    st.metric(label="Rata-rata Penyewaan Sepeda / Hari", value=f"{main_df_day['cnt'].mean():,.0f}")

# Visualisasi Nomor 1
df_cuaca = main_df_hour.copy()
st.header("Hubungan Pengaruh Cuaca & Waktu terhadap Penyewaan Sepeda Tahun 2012")
st.write("Menampilkan pengaruh suhu dan jam harian terhadap jumlah penyewaan sepeda")

korelasi_suhu = df_cuaca['temp'].corr(df_cuaca['cnt'])
suhu_puncak = df_cuaca.groupby('temp')['cnt'].mean().idxmax()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Hubungan Temperatur dan Jumlah Penyewaan Sepeda", value="Semakin Hangat = Semakin Banyak Peminat", delta=f"Skor Korelasi: {korelasi_suhu:.2f}")
with col2:
    st.metric(label="Suhu Yang Paling Disukai", value=f"{suhu_puncak:.1f} °C")

st.markdown("---")

st.subheader("Visualisasi Kepadatan Penyewaan Sepeda (Jam vs Suhu)")
st.caption("*Cara membaca:* Semakin **merah pekat** warnanya, maka pada jam dan suhu tersebut sepeda **tingginya minat penyewa sepeda**")

df_cuaca['Suhu (°C)'] = df_cuaca['temp'].round(0).astype(int)
pivot_cuaca = df_cuaca.pivot_table(index='Suhu (°C)', columns='hr', values='cnt', aggfunc='mean').fillna(0)

# Gambar Grafik
fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(pivot_cuaca, cmap='YlOrRd', cbar_kws={'label': 'Rata-Rata Sepeda Tersewa'}, ax=ax)
ax.invert_yaxis() # Suhu dingin di bawah, panas di atas

ax.set_xlabel('Jam (00:00 - 23:00)')
ax.set_ylabel('Suhu Riil (°C)')
plt.grid(False)

st.pyplot(fig)

# Visualisasi Pertanyaan Nomor 2
df_multiselect = main_df_hour.copy()
st.subheader("Jumlah Penyewaan Sepeda Berdasarkan Pilihan Jam")

opsi_jam = list(range(0, 24))
jam_terpilih = st.multiselect(
    "Pilih jam yang ingin dianalisis:",
    options=opsi_jam,
    default=[7, 8, 9, 17, 18, 19]
)

nilai_workingday = 1 if pilihan_hari == "Hari Kerja" else 0
if not jam_terpilih:
    st.warning("Silakan pilih minimal satu jam pada menu di atas untuk menampilkan data.")
else:
    df_sibuk = df_multiselect[df_multiselect['hr'].isin(jam_terpilih)]
    df_normal = df_multiselect[~df_multiselect['hr'].isin(jam_terpilih)]
    
    rata_jam_terpilih = df_sibuk['cnt'].mean() if not df_sibuk.empty else 0
    rata_jam_normal = df_normal['cnt'].mean() if not df_normal.empty else 0
    
    if rata_jam_normal> 0:
        persentase_peningkatan = ((rata_jam_terpilih - rata_jam_normal) / rata_jam_normal) * 100
    else:
        persentase_peningkatan = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Rata-rata Jam Lainnya", value=f"{rata_jam_normal:.0f} sepeda")
    with col2:
        st.metric(label="Rata-rata Jam Terpilih", value=f"{rata_jam_terpilih:.0f} sepeda")
    with col3:
        st.metric(
            label="Selisih Performa", 
            value=f"{persentase_peningkatan:.1f}%", 
            delta=f"{persentase_peningkatan:.1f}%"
        )

    st.markdown("---")
    st.subheader("Grafik Tren Hari Kerja vs Hari Libur")
    df_multiselect['day_type'] = df_multiselect['workingday'].map({1: 'Hari Kerja', 0: 'Hari Libur'})
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Grafik garis utama
    sns.lineplot(
        data=df_multiselect, 
        x='hr', 
        y='cnt', 
        hue='day_type', 
        palette={'Hari Kerja': "#347900", 'Hari Libur': "#0e4eff"},
        marker='o',
        ax=ax
    )
    
    # Garis vertikal putus-putus untuk setiap jam yang dipilih
    for j in jam_terpilih:
        ax.axvline(x=j, color='red', linestyle='--', alpha=0.4)
        
    ax.set_title('Tren Penyewaan Sepeda Berdasarkan Jam Terpilih (2012)', fontsize=12)
    ax.set_xlabel('Jam (00:00 - 23:00)')
    ax.set_ylabel('Rata-rata Jumlah Penyewaan Sepeda')
    ax.set_xticks(range(0, 24))
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(title="Status Hari")
    
    st.pyplot(fig)