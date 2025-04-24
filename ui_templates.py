import streamlit as st
import pandas as pd

from data_processing import load_data, load_ref_sku, transform_data, compute_price_advantage

df_style_format = {
    "Our Price": "R$ {:.2f}",
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

        df = df_raw.copy()

        date_range = st.date_input(
            f"📅 Datas crawleadas",
            key=f"dates_{city_name}_{store_name}",
            value=(df["crawl_date"].min(), df_raw["crawl_date"].max()),
            min_value=df["crawl_date"].min(),
            max_value=df["crawl_date"].max()
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df = df[(df["crawl_date"] >= start) & (df["crawl_date"] <= end)]

        col1, col2, col3 = st.columns(3)

        with col1:
            name_list = sorted(df["product_name"].dropna().unique())
            selected_names = st.multiselect("📦 Produto", key=f"name_{city_name}_{store_name}", options=name_list)

        if selected_names:
            df = df[df["product_name"].isin(selected_names)]

        with col2:
            ean_list = sorted(df["product_ean"].dropna().unique())
            selected_eans = st.multiselect("🔢 EANs", key=f"ean_{city_name}_{store_name}", options=ean_list)

        if selected_eans:
            df = df[df["product_ean"].isin(selected_eans)]

        with col3:
            all_stores = sorted(df["store_name"].dropna().unique())
            selected_stores = st.multiselect(
                "🏪 Outras lojas para comparação",
                key=f"stores_{city_name}_{store_name}",
                options=all_stores,
                help="Selecione quais lojas comparar com a nossa. Se nenhuma for selecionada, todas serão consideradas."
            )

        if selected_stores:
            df = df[df["store_name"].isin(selected_stores + [store_name])]

        df_raw_petyard = df[df["store_name"] == store_name]
        df_transformed = transform_data(df, store_name)

        if df_raw_petyard.empty:
            st.warning(f"⚠️ Nenhum dado disponível para a loja {store_name} no intervalo selecionado.")
            return

        not_in_store = df_sku.loc[~df_sku["Código EAN"].isin(df_raw_petyard["product_ean"]), ["Código EAN", "Nome do Produto"]]

        # 📄 Metrics
        st.write("### 📄 Índices:")
        col1, col2, col3 = st.columns(3)

        with col1:
            price_index_mean = df_transformed["Price Index (Mean)"].mean()
            st.metric(
                "Preço Médio vs Concorrentes",
                f"{price_index_mean:.2f}%",
                help="Comparação dos preços da nossa loja com a média das outras lojas.",
                border=True
            )

        with col2:
            price_index_min = df_transformed["Price Index (Min)"].mean()
            st.metric(
                "Preço Mínimo vs Concorrentes",
                f"{price_index_min:.2f}%",
                help="Comparação dos preços da nossa loja com os preços mínimos da categoria.",
                border=True
            )

        with col3:
            total_skus = len(df_sku)
            available_skus = total_skus - len(not_in_store)
            st.metric(
                "Top itens disponíveis",
                f"{available_skus} / {total_skus}",
                help="Quantos dos itens mais vendidos do Ifood estão disponíveis na nossa loja.",
                border=True
            )

        # 📈 Line Chart
        st.write("### 📉 Evolução do Índice de Preço Mínimo")
        time_series_df = df_transformed.groupby("crawl_date")["Price Index (Min)"].mean().reset_index()
        st.line_chart(time_series_df.rename(columns={"crawl_date": "Data", "Price Index (Min)": "Preço Min vs Concorrência"}).set_index("Data"))

        # 💰 Price Table
        st.write(f"### 💰 Tabela de preços - {city_name}")
        st.dataframe(df_transformed.style.format(df_style_format), use_container_width=True)

        # 🥇 Price Advantage
        st.write(f"### 🥇 Vantagem de preço - {city_name}")
        df_advantage = compute_price_advantage(df, store_name)

        if df_advantage.empty:
            st.info("Nenhuma vantagem de preço encontrada no intervalo selecionado.")
        else:
            st.write(f"Temos `{len(df_advantage["product_ean"].unique())}` produtos com preço mínimo.")
            st.dataframe(df_advantage.style.format({
                "Our Price": "R$ {:.2f}",
                "2nd Lowest Price": "R$ {:.2f}",
                "Difference": "R$ {:.2f}",
                "% Difference": "% {:.2f}"
            }))

        # ❓ Missing SKUs
        st.write(f"### ❓Tabela de produtos faltantes - {city_name}")
        st.dataframe(not_in_store, use_container_width=True)
