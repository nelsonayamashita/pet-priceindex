import pandas as pd
import streamlit as st
import boto3
from pyathena import connect
import numpy as np

SHEET_URLS = {
    "pet":{
        "SP": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1455125218"
        },
        "RJ": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=858553916"
        },
        "CWB": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=815803268"
        },
        "POA":{
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=356162678"
        },
        "BH":{
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=93894901"
        },
        "FOR":{
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1734542931"
        },
        "CAMP": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=2123440685"
        },
        "SOROCABA": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=630689705"
        },
        "JUNDIAI": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1199137498"
        },
        "FLN": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=937539626"
        }
    },
    "ice": {
        "SP": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=2000186049"
        }
    },
    "beverage": {
        "SP": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=625148883"
        }
    },
    "pharmacy": {
        "SP": {
            "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1192735632"
        }
    }
}
S3_STAGING_DIR = st.secrets["S3_STAGING_DIR"]
AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]
SCHEMA_NAME = st.secrets["SCHEMA_NAME"]
AWS_REGION = st.secrets["AWS_REGION"]


COL_TYPES = {
    "Código EAN": int,
    "product_ean": str,
    "original_price": float,
    "discount_price": float
}

@st.cache_data(ttl="1d")
def load_ref_sku(segment):
    sku_data = {}
    sheet_url = SHEET_URLS[segment]
    for city, urls in sheet_url.items():
        try:
            df = pd.read_csv(urls["sku"])

            for col, dtype in COL_TYPES.items():
                if col in df.columns:
                    try:
                        if dtype == float:
                            df[col] = (
                                df[col]
                                .astype(str)
                                .str.replace(r'[^\d,.-]', '', regex=True)
                                .str.replace(r'\.(?=\d{3}(?:\D|$))', '', regex=True)
                                .str.replace(',', '.', regex=True)
                                .replace('', '0')
                                .astype(float)
                            )
                        elif dtype == int:
                            df[col] = (
                                df[col]
                                .astype(str)
                                .str.replace(r'[^\d-]', '', regex=True)
                                .replace('', '0')
                                .astype(int)
                            )
                        else:
                            df[col] = df[col].astype(dtype)
                    except Exception as e:
                        print(f"⚠️ Erro ao converter coluna '{col}' para {dtype} em {city}: {e}")

            sku_data[city] = df
        except Exception as e:
            print(f"❌ Erro ao carregar SKU de {city}: {e}")
            sku_data[city] = pd.DataFrame()

    return sku_data

@st.cache_data(ttl="1d", show_spinner="Carregando os dados do crawler, isso pode demorar algum tempo...")
def load_data(segment):
    athena_client = boto3.client(
        "athena",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )

    conn = connect(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        s3_staging_dir=S3_STAGING_DIR,
        region_name=AWS_REGION,
    )

    query = f"""
    SELECT *
    FROM bronze.ifood_crawler_{segment}
    WHERE crawl_date >= DATE_ADD('day', -30, CURRENT_DATE)
    """

    df = pd.read_sql(query, conn, parse_dates=["crawl_date"])

    return df

@st.cache_data(ttl="1d")
def transform_data(df_raw, store_name):
    df_raw["final_price"] = df_raw["discount_price"].fillna(df_raw["original_price"])

    mean_other_stores = (
        df_raw[df_raw["store_name"] != store_name]
        .groupby(["product_name", "crawl_date"])["final_price"]
        .mean()
        .reset_index()
        .rename(columns={"final_price": "Mean Other Stores"})
    )
    min_prices = (
        df_raw.groupby(["product_name", "crawl_date"])["final_price"]
        .min()
        .reset_index()
        .rename(columns={"final_price": "Minimum Price"})
    )

    petyard_prices = df_raw[df_raw["store_name"] == store_name].copy()

    petyard_prices = petyard_prices.merge(mean_other_stores, on=["product_name", "crawl_date"], how="left")
    petyard_prices = petyard_prices.merge(min_prices, on=["product_name", "crawl_date"], how="left")

    petyard_prices["Price Index (Mean)"] = petyard_prices["final_price"] * 100 / petyard_prices["Mean Other Stores"]
    petyard_prices["Price Index (Min)"] = petyard_prices["final_price"] * 100 / petyard_prices["Minimum Price"]

    result_df = petyard_prices[[
        "product_ean",
        "product_name",
        "final_price",
        "Minimum Price",
        "Price Index (Mean)",
        "Price Index (Min)",
        "crawl_date",
    ]].copy()

    result_df = result_df.rename(columns={
        "final_price": "Our Price",
        "product_name": "Nomes",
        "product_ean": "product_ean",
    })


    return result_df

def compute_price_advantage(df_filtered, store_name):
    df_filtered["final_price"] = df_filtered["discount_price"].fillna(df_filtered["original_price"])
    df_filtered = df_filtered.dropna(subset=["product_ean", "product_name", "final_price", "crawl_date", "store_name"])
    result_rows = []

    grouped = df_filtered.groupby(["crawl_date", "product_ean"])

    for (crawl_date, ean), group in grouped:
        group_sorted = group.sort_values("final_price")
        if len(group_sorted) < 2:
            continue

        first_row = group_sorted.iloc[0]
        second_row = group_sorted.iloc[1]

        if first_row["store_name"] == store_name:
            result_rows.append({
                "product_ean": ean,
                "Nome": first_row["product_name"],
                "Our Price": first_row["final_price"],
                "2nd Lowest Price": second_row["final_price"],
                "Difference": second_row["final_price"] - first_row["final_price"],
                "% Difference": (second_row["final_price"] - first_row["final_price"]) * 100/first_row["final_price"],
                "crawl_date": crawl_date
            })

    df_result = pd.DataFrame(result_rows)
    return df_result
