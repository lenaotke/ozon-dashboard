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
            # Пытаемся прочитать файл. 
            # engine=None позволяет Pandas самому выбрать лучший движок (openpyxl или xlrd)
            df = pd.read_excel(f, engine=None) 
            df.columns = [str(c).strip() for c in df.columns]
            
            # Проверяем, прайс это или отчет
            if 'Цена продажи опт' in df.columns or 'Себестоимость' in df.columns:
                price_df = df
                st.write(f"✅ Прайс-лист загружен: {f.name}")
            else:
                dfs.append(df)
                st.write(f"✅ Отчет загружен: {f.name}")
        except Exception as e:
            st.error(f"❌ Не удалось прочитать файл {f.name}. Попробуйте открыть его в Excel, нажать 'Сохранить как' и выбрать формат 'Книга Excel (.xlsx)'. Ошибка: {e}")

    if dfs and price_df is not None:
        try:
            df_ozon = pd.concat(dfs, ignore_index=True)
            st.success("Данные успешно склеены и готовы к анализу!")
            st.write(df_ozon.head())
        except Exception as e:
            st.error(f"Ошибка при объединении таблиц: {e}")
