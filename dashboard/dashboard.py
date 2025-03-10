import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Set konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis E-commerce Brasil",
    page_icon="🛒",
    layout="wide"
)

# CSS kustom untuk memperbaiki tampilan dashboard
st.markdown("""
<style>
.main {
    background-color: #f5f5f5;
}
.st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {
    color: #1E88E5;
}
.metric-card {
    background-color: #FFFFFF;
    border-radius: 5px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Judul dashboard
st.title("🇧🇷 Dashboard Analisis E-commerce Brasil")
st.markdown("#### Wawasan dan Metrik Kinerja dari Data E-commerce (2017-2018)")

# Memuat Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dashboard/main_data.csv')
        
        # Konversi kolom tanggal ke format datetime
        date_columns = [col for col in df.columns if 'date' in col or 'timestamp' in col]
        for col in date_columns:
            if col in df.columns:
                try:
                    # Untuk tanggal dengan format "YYYY-MM-DD HH:MM:SS"
                    df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                except:
                    try:
                        # Jika format spesifik gagal, gunakan pendekatan yang lebih fleksibel
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    except Exception as e:
                        st.warning(f"Tidak dapat mengonversi kolom {col} ke format datetime: {e}")
        
        # Pastikan kolom year_month ada untuk analisis waktu
        if 'year_month' not in df.columns and 'order_purchase_timestamp' in df.columns:
            df['year_month'] = df['order_purchase_timestamp'].dt.strftime('%Y-%m')
        
        return df
    except Exception as e:
        st.error(f"Error memuat data: {e}")
        # Kembalikan dataframe kosong atau raiser error
        return pd.DataFrame()

all_df = load_data()

if all_df.empty:
    st.error("Gagal memuat data. Mohon periksa apakah 'main_data.csv' ada dan diformat dengan benar.")
    st.stop()

# Membuat filter tanggal
st.sidebar.header("📅 Filter Tanggal")

# Dapatkan tanggal min dan max untuk slider
if 'order_purchase_timestamp' in all_df.columns:
    min_date = all_df['order_purchase_timestamp'].min().date()
    max_date = all_df['order_purchase_timestamp'].max().date()
    
    # Buat slider range tanggal
    start_date, end_date = st.sidebar.date_input(
        "Pilih Rentang Tanggal:",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
else:
    # Fallback jika order_purchase_timestamp tidak tersedia
    start_date = datetime(2017, 1, 1).date()
    end_date = datetime(2018, 12, 31).date()

# Filter data berdasarkan tanggal yang dipilih
if 'order_purchase_timestamp' in all_df.columns:
    filtered_df = all_df[(all_df['order_purchase_timestamp'].dt.date >= start_date) & 
                         (all_df['order_purchase_timestamp'].dt.date <= end_date)]
else:
    filtered_df = all_df

# Membuat navigasi di sidebar
st.sidebar.header("📊 Navigasi")
analysis_options = [
    "Ikhtisar",
    "Analisis Foto Produk",
    "Analisis Cicilan Pembayaran",
    "Analisis Kinerja Pengiriman",
    "Analisis Klaster Ibitinga"
]
selected_analysis = st.sidebar.radio("Pilih Analisis:", analysis_options)

# Membuat fungsi untuk format mata uang dalam BRL
def format_brl(value):
    return f"R$ {value:,.2f}"

# Membuat fungsi utilitas untuk visualisasi yang lebih baik
def plot_bar_chart(df, x, y, title, xlabel, ylabel, color='#1E88E5', orientation='v'):
    fig = px.bar(
        df, 
        x=x if orientation == 'v' else y, 
        y=y if orientation == 'v' else x, 
        title=title,
        labels={x: xlabel, y: ylabel},
        color_discrete_sequence=[color]
    )
    
    if orientation == 'h':
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    return fig

# Fungsi untuk menambahkan kartu metrik
def metric_card(title, value, delta=None, suffix="", prefix=""):
    col = st.columns(1)[0]
    with col:
        st.markdown(f"<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(title, f"{prefix}{value}{suffix}", delta)
        st.markdown("</div>", unsafe_allow_html=True)

# Fungsi untuk membuat subjudul
def subheader(text):
    st.markdown(f"### {text}")

# 1. BAGIAN IKHTISAR
if selected_analysis == "Ikhtisar":
    subheader("📈 Ikhtisar Bisnis")
    
    # Metrik ringkasan
    total_orders = filtered_df['order_id'].nunique()
    total_revenue = filtered_df['price'].sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Hitung pertumbuhan jika data tersedia
    if 'year_month' in filtered_df.columns:
        monthly_revenue = filtered_df.groupby('year_month')['price'].sum().reset_index()
        
        if len(monthly_revenue) > 1:
            current_month = monthly_revenue.iloc[-1]['price']
            previous_month = monthly_revenue.iloc[-2]['price']
            revenue_growth = ((current_month - previous_month) / previous_month) * 100
        else:
            revenue_growth = 0
    else:
        revenue_growth = None
    
    # Tampilkan metrik dalam satu baris
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Pesanan", f"{total_orders:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Pendapatan", format_brl(total_revenue), f"{revenue_growth:.1f}%" if revenue_growth is not None else None)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Nilai Pesanan Rata-rata", format_brl(avg_order_value))
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tren penjualan sepanjang waktu
    subheader("Tren Penjualan Sepanjang Waktu")
    if 'year_month' in filtered_df.columns:
        sales_trend = filtered_df.groupby('year_month')['price'].sum().reset_index()
        sales_trend['year_month'] = pd.to_datetime(sales_trend['year_month'] + '-01')
        
        # Buat plot time series
        fig_trend = px.line(
            sales_trend, 
            x='year_month', 
            y='price',
            title='Tren Penjualan Bulanan',
            labels={'year_month': 'Bulan', 'price': 'Pendapatan (R$)'}
        )
        fig_trend.update_traces(line_color='#1E88E5', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Data deret waktu tidak tersedia untuk analisis tren.")
    
    # Kategori produk teratas
    col1, col2 = st.columns(2)
    
    with col1:
        subheader("Kategori Produk Teratas berdasarkan Pendapatan")
        if 'product_category_name' in filtered_df.columns:
            top_categories = filtered_df.groupby('product_category_name')['price'].sum().reset_index()
            top_categories = top_categories.sort_values('price', ascending=False).head(10)
            
            # Buat bagan batang horizontal
            fig_categories = plot_bar_chart(
                top_categories,
                'price',
                'product_category_name',
                '10 Kategori Teratas berdasarkan Pendapatan',
                'Pendapatan (R$)',
                'Kategori',
                color='#42A5F5',
                orientation='h'
            )
            st.plotly_chart(fig_categories, use_container_width=True)
        else:
            st.warning("Data kategori produk tidak tersedia.")
    
    with col2:
        subheader("Distribusi Status Pesanan")
        if 'order_status' in filtered_df.columns:
            status_counts = filtered_df['order_status'].value_counts().reset_index()
            status_counts.columns = ['order_status', 'count']
            
            # Buat diagram lingkaran
            fig_status = px.pie(
                status_counts, 
                values='count', 
                names='order_status',
                title='Distribusi Status Pesanan',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.warning("Data status pesanan tidak tersedia.")

# 2. ANALISIS FOTO PRODUK
elif selected_analysis == "Analisis Foto Produk":
    subheader("📸 Analisis Foto Produk")
    st.markdown("""
    Analisis ini mengeksplorasi dampak fotografi produk (jumlah foto produk) terhadap kinerja penjualan.
    """)
    
    # Periksa apakah analisis foto dimungkinkan
    if 'photo_category' in filtered_df.columns and 'price' in filtered_df.columns:
        # Filter data jika diperlukan
        photo_df = filtered_df
        
        # Tingkat konversi berdasarkan kategori foto
        conversion_by_photo = photo_df.groupby('photo_category').agg({
            'order_id': 'count',
            'price': 'mean',
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Nilai Pesanan Rata-rata berdasarkan Kategori Foto
            fig_aov = px.bar(
                conversion_by_photo,
                x='photo_category',
                y='price',
                title='Nilai Pesanan Rata-rata berdasarkan Kategori Foto',
                labels={'photo_category': 'Kategori Foto', 'price': 'Nilai Pesanan Rata-rata (R$)'},
                color='photo_category',
                color_discrete_sequence=['#1976D2', '#64B5F6', '#90CAF9']
            )
            st.plotly_chart(fig_aov, use_container_width=True)
        
        with col2:
            # Jumlah Pesanan berdasarkan Kategori Foto
            fig_orders = px.bar(
                conversion_by_photo,
                x='photo_category',
                y='order_id',
                title='Jumlah Pesanan berdasarkan Kategori Foto',
                labels={'photo_category': 'Kategori Foto', 'order_id': 'Jumlah Pesanan'},
                color='photo_category',
                color_discrete_sequence=['#1976D2', '#64B5F6', '#90CAF9']
            )
            st.plotly_chart(fig_orders, use_container_width=True)
        
        # Kategori teratas dengan manfaat tertinggi dari foto multiple
        if 'product_category_name' in photo_df.columns:
            st.markdown("### Kategori dengan Manfaat Tertinggi dari Foto Multiple")
            
            category_photo_impact = photo_df.groupby(['product_category_name', 'photo_category']).agg({
                'price': 'mean',
                'order_id': 'count'
            }).reset_index()
            
            # Pivot data untuk perbandingan
            pivot_photo = category_photo_impact.pivot(
                index='product_category_name',
                columns='photo_category',
                values='price'
            ).reset_index()
            
            # Hitung dampak - membandingkan >3 Foto dengan Foto Tunggal
            if 'Foto Tunggal' in pivot_photo.columns and '>3 Foto' in pivot_photo.columns:
                pivot_photo['price_increase'] = (pivot_photo['>3 Foto'] - pivot_photo['Foto Tunggal']) / pivot_photo['Foto Tunggal'] * 100
                pivot_photo = pivot_photo.dropna(subset=['price_increase']).sort_values('price_increase', ascending=False)
                
                top_impact_categories = pivot_photo.head(10)
                
                fig_impact = px.bar(
                    top_impact_categories,
                    x='product_category_name',
                    y='price_increase',
                    title='10 Kategori Teratas dengan Peningkatan Harga Tertinggi dari Foto Multiple',
                    labels={'product_category_name': 'Kategori Produk', 'price_increase': 'Peningkatan Harga (%)'},
                    color='price_increase',
                    color_continuous_scale='Blues'
                )
                fig_impact.update_layout(xaxis={'categoryorder':'total descending'})
                st.plotly_chart(fig_impact, use_container_width=True)
            else:
                st.warning("Data tidak cukup untuk membandingkan kategori foto yang berbeda")
    else:
        st.error("Data yang diperlukan untuk analisis foto produk tidak tersedia dalam dataset.")

# 3. ANALISIS CICILAN PEMBAYARAN
elif selected_analysis == "Analisis Cicilan Pembayaran":
    subheader("💳 Analisis Cicilan Pembayaran")
    st.markdown("""
    Analisis ini mengkaji bagaimana opsi cicilan pembayaran memengaruhi perilaku pembelian dan nilai pesanan.
    """)
    
    # Periksa apakah analisis cicilan dimungkinkan
    if 'installment_category' in filtered_df.columns and 'price' in filtered_df.columns:
        # Filter data
        installment_df = filtered_df
        
        # Nilai pesanan rata-rata berdasarkan kategori cicilan
        aov_by_installment = installment_df.groupby('installment_category')['price'].mean().reset_index()
        
        # Visualisasikan nilai pesanan rata-rata berdasarkan cicilan
        fig_aov = px.bar(
            aov_by_installment,
            x='installment_category',
            y='price',
            title='Nilai Pesanan Rata-rata berdasarkan Kategori Cicilan',
            labels={'installment_category': 'Kategori Cicilan', 'price': 'Nilai Pesanan Rata-rata (R$)'},
            color='installment_category',
            color_discrete_sequence=['#1976D2', '#42A5F5', '#64B5F6', '#90CAF9']
        )
        st.plotly_chart(fig_aov, use_container_width=True)
        
        # Penggunaan cicilan berdasarkan kategori produk
        if 'product_category_name' in installment_df.columns:
            # Hitung persentase penggunaan cicilan berdasarkan kategori
            category_installment = installment_df.groupby(['product_category_name', 'installment_category']).size().reset_index(name='count')
            category_totals = category_installment.groupby('product_category_name')['count'].sum().reset_index(name='total')
            category_installment = category_installment.merge(category_totals, on='product_category_name')
            category_installment['percentage'] = (category_installment['count'] / category_installment['total']) * 100
            
            # Filter hanya untuk Cicilan 6-12 dan kategori nilai tinggi
            if 'Cicilan 6-12' in category_installment['installment_category'].values:
                high_installment = category_installment[category_installment['installment_category'] == 'Cicilan 6-12']
                top_categories = high_installment.sort_values('percentage', ascending=False).head(10)
                
                fig_top_cat = px.bar(
                    top_categories,
                    x='product_category_name',
                    y='percentage',
                    title='10 Kategori Teratas dengan Penggunaan Cicilan 6-12 Tertinggi',
                    labels={'product_category_name': 'Kategori Produk', 'percentage': 'Persentase Pesanan (%)'},
                    color='percentage',
                    color_continuous_scale='Blues'
                )
                fig_top_cat.update_layout(xaxis={'categoryorder':'total descending'})
                st.plotly_chart(fig_top_cat, use_container_width=True)
            
            # Perbandingan peningkatan pendapatan
            if 'Pembayaran Langsung' in category_installment['installment_category'].values and 'Cicilan 6-12' in category_installment['installment_category'].values:
                st.markdown("### Dampak Pendapatan dari Cicilan 6-12 vs Pembayaran Langsung")
                
                # Pertama hitung harga rata-rata berdasarkan kategori dan cicilan
                price_by_install_cat = installment_df.groupby(['product_category_name', 'installment_category'])['price'].mean().reset_index()
                
                # Pivot untuk membandingkan harga
                price_pivot = price_by_install_cat.pivot(
                    index='product_category_name',
                    columns='installment_category',
                    values='price'
                ).reset_index()
                
                # Hitung persentase peningkatan harga
                if 'Pembayaran Langsung' in price_pivot.columns and 'Cicilan 6-12' in price_pivot.columns:
                    price_pivot['price_increase_pct'] = (price_pivot['Cicilan 6-12'] - price_pivot['Pembayaran Langsung']) / price_pivot['Pembayaran Langsung'] * 100
                    price_pivot = price_pivot.dropna(subset=['price_increase_pct']).sort_values('price_increase_pct', ascending=False)
                    
                    top_price_impact = price_pivot.head(10)
                    
                    # Buat visualisasi perbandingan
                    fig_price_impact = px.bar(
                        top_price_impact,
                        x='product_category_name',
                        y='price_increase_pct',
                        title='10 Kategori Teratas dengan Peningkatan Harga Tertinggi dari Cicilan 6-12',
                        labels={'product_category_name': 'Kategori Produk', 'price_increase_pct': 'Peningkatan Harga (%)'},
                        color='price_increase_pct',
                        color_continuous_scale='Greens'
                    )
                    fig_price_impact.update_layout(xaxis={'categoryorder':'total descending'})
                    st.plotly_chart(fig_price_impact, use_container_width=True)
    else:
        st.error("Data yang diperlukan untuk analisis cicilan pembayaran tidak tersedia dalam dataset.")

# 4. ANALISIS KINERJA PENGIRIMAN
elif selected_analysis == "Analisis Kinerja Pengiriman":
    subheader("🚚 Analisis Kinerja Pengiriman")
    st.markdown("""
    Analisis ini mengkaji dampak kinerja pengiriman terhadap kepuasan pelanggan dan ulasan.
    """)
    
    # Periksa apakah analisis pengiriman dimungkinkan
    if 'is_late_delivery' in filtered_df.columns and 'review_score' in filtered_df.columns:
        # Filter data
        delivery_df = filtered_df.dropna(subset=['is_late_delivery', 'review_score'])
        
        # Konversi boolean ke kategori jika diperlukan
        if delivery_df['is_late_delivery'].dtype == bool:
            delivery_df['delivery_status'] = delivery_df['is_late_delivery'].map({True: 'Terlambat', False: 'Tepat Waktu'})
        else:
            delivery_df['delivery_status'] = delivery_df['is_late_delivery'].map({1: 'Terlambat', 0: 'Tepat Waktu'})
        
        # Skor ulasan rata-rata berdasarkan status pengiriman
        review_by_delivery = delivery_df.groupby('delivery_status')['review_score'].mean().reset_index()
        
        # Hitung persentase pengiriman terlambat
        total_deliveries = len(delivery_df)
        late_deliveries = len(delivery_df[delivery_df['delivery_status'] == 'Terlambat'])
        late_percentage = (late_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0
        
        # Buat metrik di bagian atas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Skor Ulasan Rata-rata (Tepat Waktu)", f"{review_by_delivery[review_by_delivery['delivery_status'] == 'Tepat Waktu']['review_score'].values[0]:.2f}/5,00")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Skor Ulasan Rata-rata (Terlambat)", f"{review_by_delivery[review_by_delivery['delivery_status'] == 'Terlambat']['review_score'].values[0]:.2f}/5,00")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Persentase Pengiriman Terlambat", f"{late_percentage:.2f}%")
            st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Perbandingan skor ulasan
            fig_review = px.bar(
                review_by_delivery,
                x='delivery_status',
                y='review_score',
                title='Skor Ulasan Rata-rata berdasarkan Status Pengiriman',
                labels={'delivery_status': 'Status Pengiriman', 'review_score': 'Skor Ulasan Rata-rata'},
                color='delivery_status',
                color_discrete_map={'Tepat Waktu': '#4CAF50', 'Terlambat': '#F44336'}
            )
            st.plotly_chart(fig_review, use_container_width=True)
        
        with col2:
            # Distribusi skor ulasan
            review_dist = delivery_df.groupby(['delivery_status', 'review_score']).size().reset_index(name='count')
            review_totals = review_dist.groupby('delivery_status')['count'].sum().reset_index(name='total')
            review_dist = review_dist.merge(review_totals, on='delivery_status')
            review_dist['percentage'] = (review_dist['count'] / review_dist['total']) * 100
            
            fig_dist = px.bar(
                review_dist,
                x='review_score',
                y='percentage',
                color='delivery_status',
                barmode='group',
                title='Distribusi Skor Ulasan berdasarkan Status Pengiriman',
                labels={'review_score': 'Skor Ulasan', 'percentage': 'Persentase Ulasan (%)', 'delivery_status': 'Status Pengiriman'},
                color_discrete_map={'Tepat Waktu': '#4CAF50', 'Terlambat': '#F44336'}
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Kategori yang paling terdampak oleh pengiriman terlambat
        if 'product_category_name' in delivery_df.columns:
            st.markdown("### Kategori yang Paling Terdampak oleh Pengiriman Terlambat")
            
            # Hitung dampak pada ulasan berdasarkan kategori
            category_impact = delivery_df.groupby(['product_category_name', 'delivery_status'])['review_score'].mean().reset_index()
            
            # Pivot untuk membandingkan tepat waktu vs terlambat
            impact_pivot = category_impact.pivot(
                index='product_category_name',
                columns='delivery_status',
                values='review_score'
            ).reset_index()
            
            # Hitung penurunan skor ulasan
            impact_pivot['score_decrease'] = impact_pivot['Tepat Waktu'] - impact_pivot['Terlambat']
            impact_pivot['score_decrease_pct'] = (impact_pivot['score_decrease'] / impact_pivot['Tepat Waktu']) * 100
            impact_pivot = impact_pivot.dropna(subset=['score_decrease_pct']).sort_values('score_decrease_pct', ascending=False)
            
            top_impact = impact_pivot.head(10)
            
            fig_impact = px.bar(
                top_impact,
                x='product_category_name',
                y='score_decrease_pct',
                title='10 Kategori yang Paling Terdampak oleh Pengiriman Terlambat (% Penurunan Skor Ulasan)',
                labels={'product_category_name': 'Kategori Produk', 'score_decrease_pct': 'Penurunan Skor Ulasan (%)'},
                color='score_decrease_pct',
                color_continuous_scale='Reds'
            )
            fig_impact.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_impact, use_container_width=True)
    else:
        st.error("Data yang diperlukan untuk analisis kinerja pengiriman tidak tersedia dalam dataset.")

# 5. ANALISIS KLASTER IBITINGA
elif selected_analysis == "Analisis Klaster Ibitinga":
    subheader("🏭 Analisis Klaster Ibitinga")
    st.markdown("""
    Analisis ini mengkaji kinerja penjual dari Ibitinga dibandingkan dengan penjual dari kota-kota lain.
    """)
    
    # Periksa apakah analisis Ibitinga dimungkinkan
    if 'is_ibitinga' in filtered_df.columns and 'price' in filtered_df.columns:
        # Filter data
        ibitinga_df = filtered_df
        
        # Metrik dasar
        ibitinga_sellers = ibitinga_df[ibitinga_df['is_ibitinga']]['seller_id'].nunique()
        other_sellers = ibitinga_df[~ibitinga_df['is_ibitinga']]['seller_id'].nunique()
        
        ibitinga_revenue = ibitinga_df[ibitinga_df['is_ibitinga']]['price'].sum()
        other_revenue = ibitinga_df[~ibitinga_df['is_ibitinga']]['price'].sum()
        
        ibitinga_orders = ibitinga_df[ibitinga_df['is_ibitinga']]['order_id'].nunique()
        other_orders = ibitinga_df[~ibitinga_df['is_ibitinga']]['order_id'].nunique()
        
        # Hitung pendapatan per penjual
        revenue_per_seller_ibitinga = ibitinga_revenue / ibitinga_sellers if ibitinga_sellers > 0 else 0
        revenue_per_seller_other = other_revenue / other_sellers if other_sellers > 0 else 0
        
        # Tampilkan metrik
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Jumlah Penjual", f"Ibitinga: {ibitinga_sellers} | Lainnya: {other_sellers}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Pendapatan per Penjual (Ibitinga)", format_brl(revenue_per_seller_ibitinga))
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Pendapatan per Penjual (Kota Lain)", format_brl(revenue_per_seller_other))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Analisis per kategori
        if 'product_category_name' in ibitinga_df.columns:
            # Dapatkan kategori teratas untuk Ibitinga
            ibitinga_categories = ibitinga_df[ibitinga_df['is_ibitinga']].groupby('product_category_name')['price'].sum().nlargest(10).index.tolist()
            
            # Filter data untuk kategori-kategori tersebut
            top_cat_df = ibitinga_df[ibitinga_df['product_category_name'].isin(ibitinga_categories)]
            
            # Hitung metrik berdasarkan kategori dan tipe penjual
            cat_performance = top_cat_df.groupby(['product_category_name', 'is_ibitinga']).agg({
                'price': 'sum',
                'seller_id': pd.Series.nunique,
                'order_id': pd.Series.nunique
            }).reset_index()
            
            # Hitung pendapatan per penjual berdasarkan kategori
            cat_performance['revenue_per_seller'] = cat_performance['price'] / cat_performance['seller_id']
            
            # Pivot untuk perbandingan yang lebih mudah
            performance_pivot = cat_performance.pivot(
                index='product_category_name',
                columns='is_ibitinga',
                values=['revenue_per_seller', 'price', 'seller_id']
            )
            
            # Ratakan kolom MultiIndex
            performance_pivot.columns = [f"{col[0]}_{col[1]}" for col in performance_pivot.columns]
            performance_pivot = performance_pivot.reset_index()
            
            # Hitung perbedaan persentase
            performance_pivot['revenue_per_seller_pct_diff'] = (
                (performance_pivot['revenue_per_seller_True'] - performance_pivot['revenue_per_seller_False']) / 
                performance_pivot['revenue_per_seller_False'] * 100
            )
            
            performance_pivot = performance_pivot.sort_values('revenue_per_seller_pct_diff', ascending=False)
            
            # Buat visualisasi perbandingan
            st.markdown("### Pendapatan per Penjual: Ibitinga vs Kota Lain (Kategori Teratas)")
            
            # Siapkan data untuk visualisasi perbandingan pendapatan per penjual
            comparison_data = []
            for _, row in performance_pivot.iterrows():
                if pd.notnull(row.get('revenue_per_seller_True', np.nan)) and pd.notnull(row.get('revenue_per_seller_False', np.nan)):
                    comparison_data.extend([
                        {
                            'Category': row['product_category_name'],
                            'Seller Type': 'Ibitinga',
                            'Revenue per Seller': row['revenue_per_seller_True']
                        },
                        {
                            'Category': row['product_category_name'],
                            'Seller Type': 'Kota Lain',
                            'Revenue per Seller': row['revenue_per_seller_False']
                        }
                    ])
            
            comparison_df = pd.DataFrame(comparison_data)
            
            fig_comparison = px.bar(
                comparison_df,
                x='Category',
                y='Revenue per Seller',
                color='Seller Type',
                barmode='group',
                title='Pendapatan per Penjual: Ibitinga vs Kota Lain (Kategori Teratas)',
                labels={'Category': 'Kategori Produk', 'Revenue per Seller': 'Pendapatan per Penjual (R$)'},
                color_discrete_map={'Ibitinga': '#1E88E5', 'Kota Lain': '#FFC107'}
            )
            fig_comparison.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Analisis detail kategori cama_mesa_banho (tempat tidur, mandi & meja)
            if 'cama_mesa_banho' in ibitinga_categories:
                st.markdown("### Analisis Detail: Kategori Cama Mesa Banho (Tempat Tidur, Mandi & Meja)")
                
                # Filter data untuk kategori ini
                cmb_data = top_cat_df[top_cat_df['product_category_name'] == 'cama_mesa_banho']
                
                # Ekstrak metrik kunci
                ibitinga_cmb = cmb_data[cmb_data['is_ibitinga']]
                other_cmb = cmb_data[~cmb_data['is_ibitinga']]
                
                ibitinga_sellers_cmb = ibitinga_cmb['seller_id'].nunique()
                other_sellers_cmb = other_cmb['seller_id'].nunique()
                
                ibitinga_revenue_cmb = ibitinga_cmb['price'].sum()
                other_revenue_cmb = other_cmb['price'].sum()
                
                ibitinga_revenue_per_seller = ibitinga_revenue_cmb / ibitinga_sellers_cmb if ibitinga_sellers_cmb > 0 else 0
                other_revenue_per_seller = other_revenue_cmb / other_sellers_cmb if other_sellers_cmb > 0 else 0
                
                # Buat visualisasi dua panel
                fig = make_subplots(rows=1, cols=2, 
                                    specs=[[{"type": "bar"}, {"type": "bar"}]],
                                    subplot_titles=("Perbandingan Skala", "Perbandingan Efisiensi"))
                
                # Subplot pertama - perbandingan skala (penjual vs pendapatan)
                scale_data = pd.DataFrame({
                    'Metric': ['Jumlah Penjual', 'Total Pendapatan (K)'],
                    'Ibitinga': [ibitinga_sellers_cmb, ibitinga_revenue_cmb/1000],
                    'Kota Lain': [other_sellers_cmb, other_revenue_cmb/1000]
                })
                
                fig.add_trace(
                    go.Bar(x=scale_data['Metric'], y=scale_data['Ibitinga'], name='Ibitinga', marker_color='#1E88E5'),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Bar(x=scale_data['Metric'], y=scale_data['Kota Lain'], name='Kota Lain', marker_color='#FFC107'),
                    row=1, col=1
                )
                
                # Subplot kedua - perbandingan efisiensi (pendapatan per penjual)
                efficiency_data = pd.DataFrame({
                    'Lokasi Penjual': ['Ibitinga', 'Kota Lain'],
                    'Pendapatan per Penjual': [ibitinga_revenue_per_seller, other_revenue_per_seller]
                })
                
                fig.add_trace(
                    go.Bar(
                        x=efficiency_data['Lokasi Penjual'], 
                        y=efficiency_data['Pendapatan per Penjual'], 
                        marker_color=['#1E88E5', '#FFC107']
                    ),
                    row=1, col=2
                )
                
                # Tambahkan anotasi untuk subplot kedua
                pct_diff = ((ibitinga_revenue_per_seller / other_revenue_per_seller) - 1) * 100
                fig.add_annotation(
                    x=0.5, y=ibitinga_revenue_per_seller * 1.1,
                    text=f"{pct_diff:.1f}% lebih tinggi",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowcolor="green",
                    ax=0, ay=-40,
                    row=1, col=2
                )
                
                # Perbarui tata letak
                fig.update_layout(
                    title_text="Cama Mesa Banho: Ibitinga vs Kota Lain",
                    barmode='group',
                    height=500,
                    legend=dict(orientation="h", y=1.1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tambahkan penjelasan
                st.markdown("""
                Visualisasi ini menyoroti fenomena "David vs Goliath" dalam klaster tekstil Ibitinga:
                - **Skala**: Meskipun Ibitinga memiliki jauh lebih sedikit penjual, total pendapatan mereka sebanding dengan seluruh kota lain yang digabungkan
                - **Efisiensi**: Penjual Ibitinga menghasilkan pendapatan per penjual yang jauh lebih tinggi, menunjukkan kekuatan spesialisasi regional
                """)

# Tambahkan footer
st.markdown("---")
st.markdown("Dashboard E-commerce Brasil")