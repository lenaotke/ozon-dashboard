import streamlit as st
import pandas as pd

st.set_page_config(page_title="Умный Дашборд Ozon", layout="wide")
st.title("📊 Финансовый Дашборд Ozon")

uploaded_files = st.file_uploader("Загрузите файлы (.xlsx или .xls)", accept_multiple_files=True)

if uploaded_files:
    dfs = []
    price_df = None
    
    for f in uploaded_files:
        try:
            # Пытаемся прочитать файл через pandas, он сам подберет движок
            # Добавляем try-except для каждого файла отдельно
            df = pd.read_excel(f)
            df.columns = [str(c).strip() for c in df.columns]
            
            # Ищем прайс-лист
            if 'Цена продажи опт' in df.columns or 'Себестоимость' in df.columns:
                price_df = df
            else:
                dfs.append(df)
            st.write(f"✅ Файл {f.name} успешно прочитан.")
        except Exception as e:
            st.error(f"❌ Ошибка в файле {f.name}: {e}")

    if dfs and price_df is not None:
        try:
            df_ozon = pd.concat(dfs, ignore_index=True)
            st.success("Данные успешно склеены!")
            st.write(df_ozon.head())
        except Exception as e:
            st.error(f"Ошибка при объединении: {e}")
