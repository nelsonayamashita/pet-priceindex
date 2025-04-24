import streamlit as st
import pandas as pd
from data_processing import load_data

st.set_page_config(page_title="📊 Monitoramento Geral", layout="wide")
st.title("📊 Visão Geral - Segmentos do Ifood")

st.write("""
Por serem muitos dados, pode ser que demore para carregar. Se você só quer os dados do crawler na integra pode acessá-los no metabase:
\n  -[🐶 Crawler Pet](https://bi.hubii.co/question#eyJkYXRhc2V0X3F1ZXJ5Ijp7InF1ZXJ5Ijp7InNvdXJjZS10YWJsZSI6NDA3OH0sInR5cGUiOiJxdWVyeSIsImRhdGFiYXNlIjo1LCJpbmZvIjp7ImNhcmQtZW50aXR5LWlkIjoiT3QwMkI5MTAwWE14d19nTjlhM25YIn19LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=)
\n  -[🧊 Crawler Ice](https://bi.hubii.co/question#eyJkYXRhc2V0X3F1ZXJ5Ijp7InF1ZXJ5Ijp7InNvdXJjZS10YWJsZSI6NDA4NX0sInR5cGUiOiJxdWVyeSIsImRhdGFiYXNlIjo1LCJpbmZvIjp7ImNhcmQtZW50aXR5LWlkIjoieEh2bm9FRzkyd00tNVVaeVpxM0F1In19LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=)
\n  -[🥤 Crawler Beverage](https://bi.hubii.co/question#eyJkYXRhc2V0X3F1ZXJ5Ijp7InF1ZXJ5Ijp7InNvdXJjZS10YWJsZSI6NDA4NX0sInR5cGUiOiJxdWVyeSIsImRhdGFiYXNlIjo1LCJpbmZvIjp7ImNhcmQtZW50aXR5LWlkIjoieEh2bm9FRzkyd00tNVVaeVpxM0F1In19LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=)
""")

st.logo(
    image="imgs/hubii-icon-rounded.png",
    size="large",
    icon_image="imgs/hubii-icon-rounded.png",
)

def show_segment_data(segment_label, segment_key):
    st.subheader(segment_label)

    df = load_data(segment_key)
    if df.empty:
        st.warning(f"Nenhum dado encontrado para {segment_label}.")
        return

    date_range = st.date_input(
        f"📅 Datas - {segment_label}",
        value=(df["crawl_date"].min(), df["crawl_date"].max()),
        min_value=df["crawl_date"].min(),
        max_value=df["crawl_date"].max()
    )

    df_filtered = df.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_filtered = df_filtered[(df_filtered["crawl_date"] >= start) & (df_filtered["crawl_date"] <= end)]


    # Simple filters
    col1, col2, col3 = st.columns(3)

    with col1:
        product_options = sorted(df_filtered["product_name"].dropna().unique())
        selected_products = st.multiselect(f"📦 Produto - {segment_label}", product_options)

    if selected_products:
        df_filtered = df_filtered[df_filtered["product_name"].isin(selected_products)]

    with col2:
        ean_options = sorted(df_filtered["product_ean"].dropna().unique())
        selected_eans = st.multiselect(f"🔢 EAN - {segment_label}", ean_options)

    if selected_eans:
        df_filtered = df_filtered[df_filtered["product_ean"].isin(selected_eans)]

    with col3:
        store_options = sorted(df_filtered["store_name"].dropna().unique())
        selected_stores = st.multiselect(f"🏪 Loja - {segment_label}", store_options)

    if selected_stores:
        df_filtered = df_filtered[df_filtered["store_name"].isin(selected_stores)]


    st.dataframe(df_filtered, use_container_width=True)

    # Export
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        f"📥 Download {segment_label}",
        data=csv,
        file_name=f"{segment_key}_segment_data.csv",
        mime="text/csv"
    )

# Render all segments
show_segment_data("🐶 PET", "pet")
st.divider()
show_segment_data("🧊 ICE", "ice")
st.divider()
show_segment_data("🥤 BEVERAGE", "beverage")
