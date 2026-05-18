import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Dashboard Analisis Penyewaan Sepeda")
st.markdown('Berbagai Faktor yang Memengaruhi Jumlah Penyewaan Sepeda')

df_day = pd.read_csv('df_day.csv')
df_hour = pd.read_csv('df_hour.csv')

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

st.subheader("Tren Penyewaan Sepeda dalam Waktu Mingguan")
df_weekly_trend = main_df_day.set_index('dteday').resample(rule='W').agg({
    'cnt': 'sum',
    'casual': 'sum',
    'registered': 'sum'
})
st.line_chart(df_weekly_trend)

# Visualisasi
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Jumlah Penyewa Sepeda Berdasarkan Jam")
    hourly_pattern = main_df_hour.groupby(by='hr').agg({'cnt': 'mean'}).reset_index()
    
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.lineplot(data=hourly_pattern, x='hr', y='cnt', marker='o', ax=ax)
    ax.set_xlabel("Waktu")
    ax.set_ylabel("Rata-Rata Jumlah Penyewaan Sepeda")
    st.pyplot(fig)

with col_right:
    st.subheader("Pengaruh Cuaca Terhadap Jumlah Penyewaan Sepeda")
    weather_pattern = main_df_hour.groupby(by='weathersit').agg({'cnt': 'mean'}).reset_index()
    weather_map = {
        1: 'Cerah', 
        2: 'Mendung', 
        3: 'Cuaca Buruk Ringan', 
        4: 'Cuaca Ekstrim'
    }
    weather_pattern['weathersit'] = weather_pattern['weathersit'].map(weather_map)
    weather_pattern = weather_pattern.sort_values(by='cnt', ascending=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=weather_pattern, x='weathersit', y='cnt', palette='Blues_r', ax=ax)
    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Rata-Rata Jumlah Penyewaan Sepeda")
    st.pyplot(fig)
