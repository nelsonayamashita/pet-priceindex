import streamlit as st
import pandas as pd

from data_processing import load_data, load_ref_sku, transform_data

st.set_page_config(page_title="Monitoramento de Catálogo", layout="wide")

st.logo(
    image="imgs/hubii-icon-rounded.png",
    size="large",
    icon_image="imgs/hubii-icon-rounded.png",
)

st.title("📊 Monitoramento de Preço")

df_data = load_data()
df_sku_data = load_ref_sku()

df_sp_raw = df_data["SP"]
df_rj_raw = df_data["RJ"]
df_cwb_raw = df_data["CWB"]
df_poa_raw = df_data["POA"]
df_bh_raw = df_data["BH"]
df_for_raw = df_data["FOR"]
df_camp_raw = df_data["CAMP"]
df_sorocaba_raw = df_data["SOROCABA"]
df_jundiai_raw = df_data["JUNDIAI"]
df_fln_raw = df_data["FLN"]

df_sku_sp = df_sku_data["SP"]
df_sku_rj = df_sku_data["RJ"]
df_sku_cwb = df_sku_data["CWB"]
df_sku_poa = df_sku_data["POA"]
df_sku_bh = df_sku_data["BH"]
df_sku_for = df_sku_data["FOR"]
df_sku_camp = df_sku_data["CAMP"]
df_sku_sorocaba = df_sku_data["SOROCABA"]
df_sku_jundiai = df_sku_data["JUNDIAI"]
df_sku_fln = df_sku_data["FLN"]

df_style_format = {
    "Petyard Price": "R$ {:.2f}",
    "Price Index (Mean)": "{:.2f}%",
    "Price Index (Min)": "{:.2f}%",
    "Minimum Price": "R$ {:.2f}",
}

def create_tab(tab, city_name, store_name, df_raw, df_sku):
    with tab:
        df_raw = df_raw.dropna(subset=["crawl_date"])
        if df_raw.empty:
            st.error(f"⚠️ Nenhum dado disponível para {city_name}.")
            return

        min_date, max_date = df_raw["crawl_date"].min(), df_raw["crawl_date"].max()
        selected_date = st.date_input(
            f"📅 Intervalo de dias crawleados - {city_name}",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        start_date, end_date = map(pd.Timestamp, selected_date)

        if start_date > end_date:
            st.error("⚠️ Data inicial maior que a final. Escolha um intervalo válido.")
            return

        df_filtered = df_raw[(df_raw["crawl_date"] >= start_date) & (df_raw["crawl_date"] <= end_date)]

        df_raw_petyard = df_filtered[df_filtered["stores"] == store_name]
        df_transformed = transform_data(df_filtered, store_name)

        if df_raw_petyard.empty:
            st.warning(f"⚠️ Nenhum dado disponível para a loja {store_name} no intervalo selecionado.")
            return

        not_in_store = df_sku.loc[~df_sku["Código EAN"].isin(df_raw_petyard["eans"]), ["Código EAN", "Nome do Produto"]]

        # Display Key Metrics
        st.write("### 📄 Índices:")
        col1, col2, col3 = st.columns(3)

        with col1:
            price_index_mean = df_transformed["Price Index (Mean)"].mean()
            st.metric(
                "Price Index - Preço Médio",
                f"{price_index_mean:.2f}%",
                help="Comparação dos preços da nossa loja com a média das outras lojas.",
                border=True
            )

        with col2:
            price_index_min = df_transformed["Price Index (Min)"].mean()
            st.metric(
                "Price Index - Preço Mínimo",
                f"{price_index_min:.2f}%",
                help="Comparação dos preços da nossa loja com os preços mínimos da categoria.",
                border=True
            )

        with col3:
            total_skus = len(df_sku)
            available_skus = total_skus - len(not_in_store)
            st.metric(
                "Número de top itens na loja",
                f"{available_skus} / {total_skus}",
                help="Quantos dos itens mais vendidos do Ifood estão disponíveis na nossa loja.",
                border=True
            )

        # Display DataFrames
        st.write(f"### 💰 Tabela de preços - {city_name}")
        st.dataframe(df_transformed.style.format(df_style_format))

        st.write(f"### ❓Tabela de produtos faltantes - {city_name}")
        st.dataframe(not_in_store)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🚗 Petyard - SP",
    "🌴 Petyard - RJ",
    "🥶 Petyard - CWB",
    "🧉 Petyard - POA",
    "🧀 Petyard - BH",
    "🏖️ Petyard - FOR",
    "🌿 Petyard - CAMP",
    "🎻 Petyard - Sorocaba",
    "🏄 Galo - Floripa "
])

create_tab(tab1, "São Paulo", "Petyard  - São Paulo", df_sp_raw, df_sku_sp)
create_tab(tab2, "Rio de Janeiro", "Petyard - Rio de Janeiro", df_rj_raw, df_sku_rj)
create_tab(tab3, "Curitiba", "Petyard - Curitiba", df_cwb_raw, df_sku_cwb)
create_tab(tab4, "Porto Alegre", "Petyard - Porto Alegre", df_poa_raw, df_sku_poa)
create_tab(tab5, "Belo Horizonte", "Petlove - Belo Horizonte", df_bh_raw, df_sku_bh)
create_tab(tab6, "Fortaleza", "Petyard - Fortaleza", df_for_raw, df_sku_for)
create_tab(tab7, "Campinas", "Petyard - Campinas", df_camp_raw, df_sku_camp)
create_tab(tab8, "Sorocaba", "Petyard - Sorocaba", df_sorocaba_raw, df_sku_sorocaba)
create_tab(tab9, "Florianópolis", "AmPm Rede Galo", df_fln_raw, df_sku_fln)
