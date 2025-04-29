import streamlit as st

from data_processing import load_data, load_ref_sku
from ui_templates import create_tab

st.set_page_config(page_title="Monitoramento de Catálogo", layout="wide")

st.logo(
    image="imgs/hubii-icon-rounded.png",
    size="large",
    icon_image="imgs/hubii-icon-rounded.png",
)

st.title("📊 Monitoramento de Preço - Ifood Bebidas")

segment = "beverage"

df_data = load_data(segment)
df_sku_data = load_ref_sku(segment)

# Map of cities and metadata
city_metadata = {
    "SP": ("São Paulo", "Heineken Express"),
}

tabs = st.tabs([f"{emoji} {name}" for code, (name, _) in city_metadata.items()
                for emoji in [dict(SP="🚗")[code]]])

for tab, (code, (city_name, store_name)) in zip(tabs, city_metadata.items()):
    df_city_raw = df_data[df_data["crawler_id"] == f"{segment}-ifood-{code.lower()}-1"]
    df_sku_city = df_sku_data[code]
    create_tab(tab, city_name, store_name, df_city_raw, df_sku_city)
