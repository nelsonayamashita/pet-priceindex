import pandas as pd
import numpy as np

SHEET_URLS = {
    "SP": {
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1192128631",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1455125218"
    },
    "RJ": {
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=598379816",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=858553916"
    },
    "CWB": {
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1631798397",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=815803268"
    },
    "POA":{
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1178781389",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=356162678"
    },
    "BH":{
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1796805684",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=93894901"
    },
    "FOR":{
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1095207839",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1734542931"
    },
    "CAMP": {
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=281458802",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=2123440685"
    },
    "SOROCABA": {
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=505742746",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=630689705"
    },
    "JUNDIAI": {
        "crawler": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1798234047",
        "sku": "https://docs.google.com/spreadsheets/d/1NDm0DWPtAxlSlh5qRKF0iz9_2WbQ155ZfPY-D0nqkXo/export?format=csv&gid=1199137498"
    },
}

COL_TYPES = {
    "Código EAN": "object",
    "eans": "object",
    "original_prices": float,
    "discount_prices": float
}

def load_ref_sku():
    sku_data = {}
    for city, urls in SHEET_URLS.items():
        try:
            df = pd.read_csv(urls["sku"])

            for col, dtype in COL_TYPES.items():
                if col in df.columns:
                    try:
                        if dtype == float:
                            df[col] = (
                                df[col]
                                .str.replace(r'[^0-9]+|\.', '', regex=True)
                                .str.replace(",", ".")
                                .astype(float)
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


def load_data():
    data = {}
    for city, urls in SHEET_URLS.items():
        try:
            df = pd.read_csv(urls["crawler"], parse_dates=["crawl_date"])

            for col, dtype in COL_TYPES.items():
                if col in df.columns:
                    try:
                        if dtype == float:
                            df[col] = (
                                df[col]
                                .str.replace(r'[^0-9.]+|\.', '', regex=True)
                                .str.replace(",", ".")
                                .astype(float)
                            )
                        else:
                            df[col] = df[col].astype(dtype)
                    except Exception as e:
                        print(f"⚠️ Erro ao converter coluna '{col}' para {dtype} em {city}: {e}")

            data[city] = df
        except Exception as e:
            print(f"❌ Erro ao carregar dados de {city}: {e}")
            data[city] = pd.DataFrame()

    return data


def transform_data(df_raw, store_name):
    df_raw["final_price"] = df_raw["discount_prices"].fillna(df_raw["original_prices"])

    mean_other_stores = (
        df_raw[df_raw["stores"] != store_name]
        .groupby(["names", "crawl_date"])["final_price"]
        .mean()
        .reset_index()
        .rename(columns={"final_price": "Mean Other Stores"})
    )
    min_prices = (
        df_raw.groupby(["names", "crawl_date"])["final_price"]
        .min()
        .reset_index()
        .rename(columns={"final_price": "Minimum Price"})
    )

    petyard_prices = df_raw[df_raw["stores"] == store_name].copy()

    petyard_prices = petyard_prices.merge(mean_other_stores, on=["names", "crawl_date"], how="left")
    petyard_prices = petyard_prices.merge(min_prices, on=["names", "crawl_date"], how="left")

    petyard_prices["Price Index (Mean)"] = petyard_prices["final_price"] * 100 / petyard_prices["Mean Other Stores"]
    petyard_prices["Price Index (Min)"] = petyard_prices["final_price"] * 100 / petyard_prices["Minimum Price"]

    result_df = petyard_prices[[
        "eans",
        "names",
        "final_price",
        "Minimum Price",
        "Price Index (Mean)",
        "Price Index (Min)",
        "crawl_date",
    ]].copy()

    result_df = result_df.rename(columns={
        "final_price": "Petyard Price",
        "names": "Nomes",
        "eans": "Eans",
    })


    return result_df