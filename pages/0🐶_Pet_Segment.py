import streamlit as st

from data_processing import load_data, load_ref_sku
from ui_templates import create_tab

st.set_page_config(page_title="Monitoramento de Catálogo", layout="wide")

st.logo(
    image="imgs/hubii-icon-rounded.png",
    size="large",
    icon_image="imgs/hubii-icon-rounded.png",
)

st.title("📊 Monitoramento de Preço - Ifood")

df_data = load_data("pet")
df_sku_data = load_ref_sku("pet")

# Map of cities and metadata
city_metadata = {
    "SP": ("São Paulo", "Petyard  - São Paulo"),
    "RJ": ("Rio de Janeiro", "Petyard - Rio de Janeiro"),
    "CWB": ("Curitiba", "Petyard - Curitiba"),
    "POA": ("Porto Alegre", "Petyard - Porto Alegre"),
    "BH": ("Belo Horizonte", "Petlove - Belo Horizonte"),
    "FOR": ("Fortaleza", "Petyard - Fortaleza"),
    "CAMP": ("Campinas", "Petyard - Campinas"),
    "SOROCABA": ("Sorocaba", "Petyard - Sorocaba"),
}

tabs = st.tabs([f"{emoji} {name}" for code, (name, _) in city_metadata.items()
                for emoji in [dict(SP="🚗", RJ="🌴", CWB="🥶", POA="🧉", BH="🧀", FOR="🏖️", CAMP="🌿", SOROCABA="🎻")[code]]])

for tab, (code, (city_name, store_name)) in zip(tabs, city_metadata.items()):
    df_city_raw = df_data[df_data["crawler_id"] == f"pet-ifood-{code.lower()}-1"]
    df_sku_city = df_sku_data[code]
    create_tab(tab, city_name, store_name, df_city_raw, df_sku_city)
