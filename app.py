import streamlit as st
import pandas as pd

st.set_page_config(page_title="Умный Дашборд Ozon", layout="wide")
st.title("📊 Финансовый Дашборд Ozon")

uploaded_files = st.file_uploader("Перетащите сюда все отчеты", accept_multiple_files=True)

if uploaded_files:
    dfs = []
    price_df = None
    
    for f in uploaded_files:
        try:
            # Читаем файл
            df = pd.read_excel(f)
            
            # Умный поиск колонки артикула
            art_col = next((c for c in df.columns if "артикул" in str(c).lower()), None)
            
            if art_col:
                df = df.rename(columns={art_col: "Артикул"})
                df["Артикул"] = df["Артикул"].astype(str).str.strip()
                
                # Ищем прайс (ищем колонку с ценой)
                if any("цена продажи опт" in str(c).lower() or "себестоимость" in str(c).lower() for c in df.columns):
                    price_df = df
                else:
                    dfs.append(df)
                st.write(f"✅ Файл {f.name} прочитан. Артикулы найдены.")
            else:
                st.warning(f"⚠️ В файле {f.name} не найдена колонка 'Артикул'.")
                
        except Exception as e:
            st.error(f"❌ Ошибка в {f.name}: {e}")

    if dfs and price_df is not None:
        try:
            df_ozon = pd.concat(dfs, ignore_index=True)
            # Финальное сведение
            merged = pd.merge(df_ozon, price_df[["Артикул", "Цена продажи опт"]], on="Артикул", how="inner")
            st.success("✅ Данные готовы!")
            st.dataframe(merged.head())
        except Exception as e:
            st.error(f"Ошибка сведения: {e}")
